import os
import shutil
from config import INITIAL_SCENARIO_RECORD_DIR, RECORDS_DIR

if __name__ == '__main__':
    target_dir = INITIAL_SCENARIO_RECORD_DIR
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(RECORDS_DIR, target_dir)
