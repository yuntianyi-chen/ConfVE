# PYTHONPATH=src python src/tools/scenario_trimmer/main.py

import multiprocessing as mp
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from cyber_record.record import Record

from config import PROJECT_ROOT

SRC_RECORDS_ROOT = "/Users/yuqihuai/Downloads/to_be_trimmed"
DST_RECORD_ROOT = f"{PROJECT_ROOT}/out/trimmed_records"
MAPS_ROOT = f"{PROJECT_ROOT}/data/maps"
NUM_WORKERS = 10


@dataclass
class TrimTask:
    __slots__ = ["src", "dst"]
    src: Path
    dst: Path


def trim_worker(queue: "mp.Queue[Optional[TrimTask]]"):
    while True:
        task = queue.get()
        if task is None:
            break
        trim_record(task.src, task.dst)


def trim_record(filename: Path, output: Path):
    record = Record(filename)
    rr_time = None
    out_msgs = list()
    for topic, msg, t in record.read_messages():
        curr_t = datetime.fromtimestamp(t / 1e9)
        if topic == "/apollo/routing_response":
            rr_time = curr_t
        if rr_time is not None and curr_t - rr_time < timedelta(seconds=30):
            out_msgs.append((topic, msg, t))

    with Record(output, mode="w") as out_record:
        for topic, msg, t in out_msgs:
            out_record.write(topic, msg, t)


def trim_directory(directory: Path):
    records = list(directory.glob("*.00000"))
    out_dir = Path(DST_RECORD_ROOT, f"{directory.name}_trimmed")
    if not out_dir.exists():
        out_dir.mkdir(parents=True)

    with mp.Manager() as manager:
        queue: "mp.Queue[Optional[TrimTask]]" = manager.Queue()
        for index, record in enumerate(records):
            queue.put(TrimTask(record, Path(out_dir, f"{index:08}.00000")))
        for _ in range(NUM_WORKERS):
            queue.put(None)
        pool = mp.Pool(NUM_WORKERS, trim_worker, (queue,))
        pool.close()
        pool.join()


def main():
    for exp in Path(SRC_RECORDS_ROOT).iterdir():
        if not exp.is_dir():
            continue
        print(f"[{datetime.now()}] Trimming {exp.name}")
        trim_directory(exp)


if __name__ == "__main__":
    main()
