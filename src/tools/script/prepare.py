import os
import shutil
from config import ADS_ROOT, PROJECT_ROOT

RECORDS_DIR = f'{PROJECT_ROOT}/data/records'

if __name__ == '__main__':
    target_dir = f"{ADS_ROOT}/initial"
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(RECORDS_DIR, target_dir)