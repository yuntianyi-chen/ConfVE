import os
import subprocess

from config import (AV_TESTING_APPROACH, BACKUP_CONFIG_SAVE_DIR,
                    BACKUP_RECORD_SAVE_DIR, DIR_ROOT, EXP_BASE_DIR, MAP_NAME,
                    MAX_RECORD_TIME, OPT_MODE)

if __name__ == "__main__":
    if (
        os.path.exists(EXP_BASE_DIR)
        and os.path.exists(BACKUP_RECORD_SAVE_DIR)
        and os.path.exists(BACKUP_CONFIG_SAVE_DIR)
    ):
        exp_out = f"{DIR_ROOT}/{AV_TESTING_APPROACH}_{MAP_NAME}_{MAX_RECORD_TIME}_{OPT_MODE}_exp_results.zip"
        records_out = f"{DIR_ROOT}/{AV_TESTING_APPROACH}_{MAP_NAME}_{MAX_RECORD_TIME}_{OPT_MODE}_records.zip"
        config_out = f"{DIR_ROOT}/{AV_TESTING_APPROACH}_{MAP_NAME}_{MAX_RECORD_TIME}_{OPT_MODE}_config.zip"
        cmds = [
            f"cd {EXP_BASE_DIR} && zip -r {exp_out} ./*",
            f"cd {BACKUP_RECORD_SAVE_DIR} && zip -r {records_out} ./*",
            f"cd {BACKUP_CONFIG_SAVE_DIR} && zip -r {config_out} ./*",
        ]

        for cmd in cmds:
            subprocess.call(cmd, shell=True)

    else:
        print("Did you run the experiment?")
