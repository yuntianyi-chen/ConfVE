import os
import shutil
import subprocess
import warnings

from config import PROJECT_ROOT
from main import confve_main
from tools.script.zip_result import zip_result

warnings.filterwarnings('ignore')


def move_file(source_dir, target_dir):
    if os.path.exists(target_dir):
        os.remove(target_dir)
    shutil.copy(source_dir, target_dir)


if __name__ == '__main__':
    subprocess.run(f"cd {PROJECT_ROOT} && make dpurge", shell=True)
    subprocess.run("python3 main.py", shell=True)
    zip_result()

    move_file("./tools/config_py/config.py", "config.py")

    subprocess.run(f"cd {PROJECT_ROOT} && make dpurge", shell=True)
    subprocess.run("python3 main.py", shell=True)
    zip_result()
