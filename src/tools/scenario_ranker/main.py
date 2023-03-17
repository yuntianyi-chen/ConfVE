# PYTHONPATH=src python src/tools/scenario_ranker/main.py

import multiprocessing as mp
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
from cyber_record.record import Record
from deap import base
from deap.tools import sortLogNondominated
from shapely.geometry import LineString

from config import PROJECT_ROOT
from environment.MapLoader import MapLoader
from objectives.violation_number.oracles import RecordAnalyzer
from tools.scenario_ranker.utils import (find_exps, find_records,
                                         get_map_name_for_exp)
from tools.utils import extract_main_decision

SRC_RECORDS_ROOT = "/Users/yuqihuai/Downloads/experiments"
DST_RECORD_ROOT = f"{PROJECT_ROOT}/out/ranked_records"
MAPS_ROOT = f"{PROJECT_ROOT}/data/maps"
NUM_WORKERS = 10


class RecordFitness(base.Fitness):
    # weighted oracle, decision, sinuosity
    weights = (1.0, 1.0, 1.0)


@dataclass
class RecordFile:
    index: int
    filename: Path
    fitness: RecordFitness = field(default_factory=RecordFitness)


def analyzer_worker(
    map_name: str, queue: "mp.Queue[Optional[Path]]", result_queue: "mp.Queue[Dict]"
):
    verbose = False
    while True:
        item = queue.get()
        if item is None:
            break
        index, total, filename = item
        if verbose:
            print(f"[{datetime.now()}] Working on {index}/{total}")
        analysis = analyze_record(map_name, filename)
        result_queue.put(analysis)


def analyze_record(map_name: str, record_file: Path) -> Dict:
    MapLoader(map_name).load_map_data()
    ra = RecordAnalyzer(record_file)
    ra.analyze()
    feature_violation = ra.oracle_manager.get_counts_wrt_oracle()
    record = Record(record_file)
    decisions: Set[Tuple] = set()
    for _, msg, _ in record.read_messages("/apollo/planning"):
        decisions = decisions | extract_main_decision(msg)
    feature_decision = {"decisions": len(decisions)}

    coordinates: List[Tuple[float, float]] = list()
    for _, msg, t in record.read_messages("/apollo/localization/pose"):
        new_coordinate = (msg.pose.position.x, msg.pose.position.y)
        if len(coordinates) > 0 and coordinates[-1] == new_coordinate:
            continue
        else:
            coordinates.append(new_coordinate)
    if len(coordinates) < 2:
        sinuosity = 0
    else:
        ego_trajectory = LineString(coordinates)
        start_point = ego_trajectory.interpolate(0, normalized=True)
        end_point = ego_trajectory.interpolate(1, normalized=True)
        shortest_path = LineString([start_point, end_point])
        sinuosity = ego_trajectory.length / shortest_path.length
    feature_sinuosity = {"sinuosity": sinuosity}

    # result = feature_violation | feature_decision | feature_sinuosity
    result = dict(**feature_violation, **feature_decision, **feature_sinuosity)
    result["filename"] = str(record_file)
    return result


def analyze_experiment(exp_path: Path, rerun: bool = False):
    print(f"[{datetime.now()}] Working on {exp_path.name}")
    map_name = get_map_name_for_exp(exp_path.name)
    record_files = find_records(exp_path)
    total_records = len(record_files)
    result = list()
    output_dir = Path(DST_RECORD_ROOT, exp_path.name)
    output_file = Path(output_dir, "_rank.csv")
    if output_file.exists() and not rerun:
        return output_file

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with mp.Manager() as manager:
        queue = manager.Queue()
        output = manager.Queue()
        pool = mp.Pool(
            NUM_WORKERS,
            analyzer_worker,
            (
                map_name,
                queue,
                output,
            ),
        )
        for index, record_file in zip(range(len(record_files)), record_files):
            queue.put((index + 1, total_records, record_file))
        for _ in range(NUM_WORKERS):
            queue.put(None)
        pool.close()
        pool.join()
        while not output.empty():
            result.append(output.get())

    df = pd.DataFrame(result)
    df.to_csv(output_file, index=False)
    return output_file


def rank_experiment(analysis: Path, select_top_k=150):
    print(f"[{datetime.now()}] Ranking {analysis}")
    df = pd.read_csv(analysis)
    oracle_columns = [x for x in df.columns if "Oracle" in x]
    weighted = list(
        zip(
            oracle_columns,
            [(len(df) - len(df[df[x] > 0])) / len(df) for x in oracle_columns],
        )
    )

    def compute_score(_row):
        score = 0.0
        for oracle_name, weight in weighted:
            score += _row[oracle_name] * weight
        return score

    df["score"] = df.apply(compute_score, axis=1)

    inds: List[Record] = list()
    for index, row in df.iterrows():
        if row.ModuleOracle > 0:
            continue
        inds.append(
            RecordFile(
                index,
                Path(row.filename),
                RecordFitness((row.score, row.decisions, row.sinuosity)),
            )
        )

    fronts = sortLogNondominated(inds, select_top_k)
    results = list()
    for front in fronts:
        for ind in front:
            results.append(ind)

    output = Path(analysis.parent, "_sorted.csv")
    df.loc[[x.index for x in results], :].to_csv(output)
    return output


def move_records(rank_file: Path):
    print(f"[{datetime.now()}] Moving records {rank_file}")
    df = pd.read_csv(rank_file)
    for index, row in df.iterrows():
        src = Path(row.filename)
        dst = Path(rank_file.parent, f"{index:08}.00000")
        if not dst.exists():
            shutil.copy(src, dst)


def zip_records(record_dir: Path):
    print(f"[{datetime.now()}] Zipping records {record_dir}")
    dst = Path(record_dir.parent, f"{record_dir.name}")
    shutil.make_archive(
        base_name=dst,
        format="zip",
        root_dir=record_dir.parent,
        base_dir=record_dir.name,
    )


def main():
    # prepare output directory
    if not os.path.exists(DST_RECORD_ROOT):
        os.makedirs(DST_RECORD_ROOT)
    for experiment in find_exps(Path(SRC_RECORDS_ROOT)):
        analysis_file = analyze_experiment(experiment)
        rank_file = rank_experiment(analysis_file)
        move_records(rank_file)
        zip_records(rank_file.parent)


if __name__ == "__main__":
    main()
