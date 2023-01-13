import os
import shutil

from config import MY_SCRIPTS_DIR, PROJECT_ROOT

target_scripts_dir = f"{MY_SCRIPTS_DIR}/ddd"
if not os.path.exists(target_scripts_dir):
    source_scripts_dir = f"{PROJECT_ROOT}/data/scripts"
    shutil.copytree(source_scripts_dir, target_scripts_dir)