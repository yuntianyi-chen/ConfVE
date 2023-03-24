import os
import shutil
import subprocess
from config import BACKUP_CONFIG_SAVE_DIR, BACKUP_RECORD_SAVE_DIR, DIR_ROOT, EXP_BASE_DIR, EXP_NAME_OPT_MODE


def zip_result():
    if (
            os.path.exists(EXP_BASE_DIR)
            and os.path.exists(BACKUP_RECORD_SAVE_DIR)
            and os.path.exists(BACKUP_CONFIG_SAVE_DIR)
    ):
        exp_files_path = f"{EXP_BASE_DIR}/{os.listdir(EXP_BASE_DIR)[-1]}"

        exp_target_dir_path = f"{exp_files_path}/{EXP_NAME_OPT_MODE}"
        if not os.path.exists(exp_target_dir_path):
            os.mkdir(exp_target_dir_path)

        for exp_file in os.listdir(exp_files_path):
            if exp_file != EXP_NAME_OPT_MODE:
                shutil.move(f"{exp_files_path}/{exp_file}", f"{exp_target_dir_path}/{exp_file}")

        exp_out = f"{DIR_ROOT}/{EXP_NAME_OPT_MODE}_exp_results.zip"

        cmd = f"cd {exp_files_path} && zip -r {exp_out} ./*"

        subprocess.call(cmd, shell=True)

        for exp_file in os.listdir(exp_target_dir_path):
            shutil.move(f"{exp_target_dir_path}/{exp_file}", f"{exp_files_path}/{exp_file}")
        os.rmdir(exp_target_dir_path)

        config_out = f"{DIR_ROOT}/{EXP_NAME_OPT_MODE}_config.zip"
        records_out = f"{DIR_ROOT}/{EXP_NAME_OPT_MODE}_records.zip"
        cmds = [
            f"cd {BACKUP_CONFIG_SAVE_DIR} && zip -r {config_out} ./*",
            f"cd {BACKUP_RECORD_SAVE_DIR} && zip -r {records_out} ./*",
        ]

        for cmd in cmds:
            subprocess.call(cmd, shell=True)

    else:
        print("Did you run the experiment?")


if __name__ == "__main__":
    zip_result()
