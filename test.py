import glob
import os
import shutil
import subprocess

from config import APOLLO_ROOT, MAGGIE_ROOT
from environment.container_settings import get_container_name

with open(f"{MAGGIE_ROOT}/violation_results.txt", "a") as f:
    f.write(f"Violation Results: \n")
    f.write(f"  record_path\n")