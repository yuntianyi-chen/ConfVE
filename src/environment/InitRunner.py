import os
import shutil
from config import MY_SCRIPTS_DIR, PROJECT_ROOT, FLAGFILE_PATH, MAP_NAME, \
    DEFAULT_CONFIG_FILE_PATH, CURRENT_CONFIG_FILE_PATH, APOLLO_MAP_DATA_DIR, MAP_DIR, APOLLO_ROOT


class InitRunner:
    def __init__(self):
        # move_scripts()
        self.move_dir(MAP_DIR, f"{APOLLO_MAP_DATA_DIR}/{MAP_NAME}")
        # self.move_dir(f"{PROJECT_ROOT}/data/scripts", MY_SCRIPTS_DIR)
        self.move_scripts()
        self.change_map_file()
        self.move_file(DEFAULT_CONFIG_FILE_PATH, CURRENT_CONFIG_FILE_PATH)
        self.move_file(f"{PROJECT_ROOT}/data/scripts/apollo_multi_container/dev_start.sh", f"{APOLLO_ROOT}/docker/scripts/dev_start.sh")

    def move_file(self, source_dir, target_dir):
        if os.path.exists(target_dir):
            os.remove(target_dir)
        shutil.copy(source_dir, target_dir)

    def change_map_file(self):
        with open(FLAGFILE_PATH, "a") as f:
            f.write(f"\n--map_dir=/apollo/modules/map/data/{MAP_NAME}\n")

    def move_scripts(self):
        for file_name in os.listdir(f"{PROJECT_ROOT}/data/scripts"):
            if ".sh" in file_name:
                self.move_file(f"{PROJECT_ROOT}/data/scripts/{file_name}", f"{MY_SCRIPTS_DIR}/{file_name}")

    def move_dir(self, source_dir, target_dir):
        if not os.path.exists(target_dir):
            shutil.copytree(source_dir, target_dir)
