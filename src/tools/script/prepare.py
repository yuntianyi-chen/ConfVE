import os
import shutil
from config import RECORDS_DIR, APOLLO_ROOT

if __name__ == '__main__':
    target_dir = f"{APOLLO_ROOT}/initial"
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(RECORDS_DIR, target_dir)
