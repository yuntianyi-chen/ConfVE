import os
import shutil
import warnings
from main import confve_main

warnings.filterwarnings('ignore')


def move_file(source_dir, target_dir):
    if os.path.exists(target_dir):
        os.remove(target_dir)
    shutil.copy(source_dir, target_dir)


if __name__ == '__main__':
    confve_main()
    move_file("./tools/config_py/config.py", "config.py")
    os.system("../Makefile")
    confve_main()
