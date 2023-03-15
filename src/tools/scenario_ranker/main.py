# PYTHONPATH=src python src/tools/scenario_ranker/main.py

import multiprocessing as mp
import os
from pathlib import Path
from typing import Dict

import pandas as pd

from config import PROJECT_ROOT
from tools.hdmap.MapParser import MapParser
from tools.scenario_ranker.utils import (find_exps, find_records,
                                         get_map_name_for_exp)

SRC_RECORDS_ROOT = "/Users/yuqihuai/Downloads/experiments"
DST_RECORD_ROOT = f"{PROJECT_ROOT}/out/ranked_records"
MAPS_ROOT = f"{PROJECT_ROOT}/data/maps"
NUM_WORKERS = 5


def analyzer_worker(queue: "mp.Queue[Path|None]", result_queue: "mp.Queue[Dict]"):
    counter = 0
    while True:
        filename = queue.get()
        if filename is None:
            break
        result_queue.put({"filename": str(filename.resolve())})
        counter += 1


def analyze_experiment(exp_path: Path):
    map_name = get_map_name_for_exp(exp_path.name)
    MapParser(os.path.join(MAPS_ROOT, map_name, "base_map.bin"))
    record_files = find_records(exp_path)
    result = list()
    output_dir = Path(DST_RECORD_ROOT, exp_path.name)
    print(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with mp.Manager() as manager:
        queue: "mp.Queue[Path|None]" = manager.Queue()
        output: "mp.Queue[Dict]" = manager.Queue()
        pool = mp.Pool(
            NUM_WORKERS,
            analyzer_worker,
            (
                queue,
                output,
            ),
        )
        for record_file in record_files:
            queue.put(record_file)
        for _ in range(NUM_WORKERS):
            queue.put(None)
        pool.close()
        pool.join()
        while not output.empty():
            result.append(output.get())

    df = pd.DataFrame(result)
    df.to_csv(Path(output_dir, "_rank.csv"), index=False)
    # print(df)


def main():
    # prepare output directory
    if not os.path.exists(DST_RECORD_ROOT):
        os.makedirs(DST_RECORD_ROOT)
    for experiment in find_exps(Path(SRC_RECORDS_ROOT)):
        analyze_experiment(experiment)
        # break


if __name__ == "__main__":
    main()
