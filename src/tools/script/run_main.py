import os
import shutil


def move_file(source_dir, target_dir):
    if os.path.exists(target_dir):
        os.remove(target_dir)
    shutil.copy(source_dir, target_dir)


if __name__ == '__main__':
    os.system("python3 main.py")
    move_file("tools/config_py/config.py", "config.py")
    # also need to move initial dir
    os.system("python3 main.py")
