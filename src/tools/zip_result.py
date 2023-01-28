from config import AV_TESTING_APPROACH, DIR_ROOT, EXP_BASE_DIR
from config import BACKUP_RECORD_SAVE_DIR, MAP_NAME, MAX_RECORD_TIME, OPT_MODE
import subprocess
import os

if __name__ == '__main__':
    if os.path.exists(EXP_BASE_DIR) and os.path.exists(BACKUP_RECORD_SAVE_DIR):
        exp_out     = f"{DIR_ROOT}/{AV_TESTING_APPROACH}_{MAP_NAME}_{MAX_RECORD_TIME}_{OPT_MODE}_exp_results.zip"
        records_out = f"{DIR_ROOT}/{AV_TESTING_APPROACH}_{MAP_NAME}_{MAX_RECORD_TIME}_{OPT_MODE}_records.zip"
        subprocess.call(f'zip -r -j  {exp_out} {EXP_BASE_DIR}'.split())

        for dest_file, src_dir in zip([exp_out, records_out], [EXP_BASE_DIR, BACKUP_RECORD_SAVE_DIR]):
            subprocess.call(f'zip -r -j {dest_file} {src_dir}'.split())
    else:
        print('Did you run the experiment?')