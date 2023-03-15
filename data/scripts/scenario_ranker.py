# PYTHONPATH=src python data/scripts/scenario_ranker.py

import os
import shutil
import string
from pathlib import Path
import pandas as pd
from loguru import logger
from nanoid import generate
from objectives.violation_number.oracles import RecordAnalyzer
from tools.hdmap.MapParser import MapParser
from config import PROJECT_ROOT

SRC_RECORDS_ROOT = '/Users/yuqihuai/Downloads/experiments'
DST_RECORD_ROOT = f'{PROJECT_ROOT}/data/ranked_records'
MAPS_ROOT = f'{PROJECT_ROOT}/data/maps'


def generate_file_id(size=12):
    return generate(string.ascii_letters+string.digits, size=size)


def list_directories(root: Path):
    assert root.is_dir(), 'root should be directory'
    for p in os.listdir(root):
        full_path = Path(os.path.join(root, p))
        if full_path.is_dir():
            yield full_path


def find_exps(root: Path):
    return list_directories(root)


def find_records(root: Path):
    return list(root.rglob("*.00000"))


def main():
    src_root = Path(SRC_RECORDS_ROOT)
    dst_root = Path(DST_RECORD_ROOT)

    for exp in find_exps(src_root):
        logger.info(f'Working on {exp.name}')

        # load map map
        current_map = ''
        for map_dir in os.listdir(MAPS_ROOT):
            if map_dir in exp.name:
                current_map = map_dir
        assert current_map != '', f'Map not found for {exp.name}'
        MapParser(os.path.join(MAPS_ROOT, current_map, 'base_map.bin'))

        # create output directory
        exp_dst = Path(os.path.join(dst_root, exp.name))
        if not os.path.exists(exp_dst):
            os.makedirs(exp_dst)

        # start analyzing
        rank_sheet = Path(os.path.join(exp_dst, '_rank.csv'))
        sorted_rank_sheet = Path(os.path.join(exp_dst, '_sorted_rank.csv'))
        if os.path.exists(rank_sheet):
            data = pd.read_csv(rank_sheet, index_col=0).to_dict(orient='index')
        else:
            data = dict()
        record_files = find_records(exp)
        for index, record_file in enumerate(record_files):
            if str(record_file.absolute()) in data:
                logger.info(f'Skipped {exp.name}/{record_file.name} ({index+1}/{len(record_files)})')
                continue
            logger.info(f'Working on {exp.name}/{record_file.name} ({index+1}/{len(record_files)})')
            try:
                ra = RecordAnalyzer(record_file.absolute())
                ra.analyze()
                features = ra.oracle_manager.get_counts_wrt_oracle()
                if features['ModuleOracle'] > 0:
                    # ModuleOracle will mask other violation
                    continue
                features['TotalCount'] = sum(features.values())
                features['UniqueCount'] = len([x for x in features.values() if x > 0])
                features['Filename'] = str(record_file.absolute())
                data[str(record_file.absolute())] = features
            except:
                logger.error(f'Error on {record_file.absolute()}')

            df = pd.DataFrame.from_dict(data, orient='index')
            df.to_csv(rank_sheet)

        # start sorting
        df = pd.read_csv(rank_sheet, index_col=0)
        columns = list(df.columns[:-3])
        weighted = list(zip(
            columns,
            [(len(df) - len(df[df[x] > 0])) / len(df) for x in columns]
        ))

        def compute_score(_row):
            score = 0.0
            for oracle_name, weight in weighted:
                score += _row[oracle_name] * weight
            return score

        df['score'] = df.apply(compute_score, axis=1)
        df.sort_values(['score', 'TotalCount', 'UniqueCount'], inplace=True, ascending=False)

        # move files
        df['dst_filename'] = ['{:08}.00000'.format(i) for i in range(len(df))]
        logger.info(f'Moving files to {exp_dst.name}')
        for index, row in df.iterrows():
            # move file
            shutil.copy2(row.Filename, os.path.join(exp_dst, row.dst_filename))
        df = df.set_index('dst_filename').drop(['Filename'], axis=1)
        df.to_csv(sorted_rank_sheet)


if __name__ == '__main__':
    main()
