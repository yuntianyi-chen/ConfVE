import os
import shutil
import warnings
from main import confve_main
from tools.script.zip_result import zip_result

warnings.filterwarnings('ignore')


def move_file(source_dir, target_dir):
    if os.path.exists(target_dir):
        os.remove(target_dir)
    shutil.copy(source_dir, target_dir)


if __name__ == '__main__':
    confve_main()

    zip_result()

    os.system("../Makefile")

    move_file("./tools/config_py/config.py", "config.py")
    confve_main()
