import os
from pathlib import Path

from config import PROJECT_ROOT

MAP_DIR = f"{PROJECT_ROOT}/data/maps"


def list_directories(root: Path):
    assert root.is_dir(), "root should be directory"
    for p in os.listdir(root):
        full_path = Path(os.path.join(root, p))
        if full_path.is_dir():
            yield full_path


def find_exps(root: Path):
    return list_directories(root)


def find_records(root: Path):
    return list(root.rglob("*.00000"))


def get_map_name_for_exp(exp_name: str):
    current_map = ""
    for map_dir in os.listdir(MAP_DIR):
        if map_dir in exp_name:
            current_map = map_dir
    assert current_map != "", f"Map not found for {exp_name}"
    return current_map
