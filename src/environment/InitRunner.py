import os
import shutil
from config import MY_SCRIPTS_DIR, PROJECT_ROOT, FLAGFILE_PATH, MAP_NAME, \
    DEFAULT_CONFIG_FILE_PATH, CURRENT_CONFIG_FILE_PATH, ADS_MAP_DATA_DIR, MAP_DIR, ADS_ROOT, \
    AUTOWARE_CURRENT_CONFIG_DIR_PATH, AUTOWARE_DEFAULT_CONFIG_DIR_PATH


class InitRunner:
    def __init__(self):
        self.delete_dir(AUTOWARE_CURRENT_CONFIG_DIR_PATH, False)
        self.move_dir(AUTOWARE_DEFAULT_CONFIG_DIR_PATH, AUTOWARE_CURRENT_CONFIG_DIR_PATH)
        # self.move_dir(MAP_DIR, f"{APOLLO_MAP_DATA_DIR}/{MAP_NAME}")
        # self.move_scripts()
        # self.change_map_file()
        # self.move_file(DEFAULT_CONFIG_FILE_PATH, CURRENT_CONFIG_FILE_PATH)
        # self.move_file(f"{PROJECT_ROOT}/data/scripts/apollo_multi_container/dev_start.sh", f"{APOLLO_ROOT}/docker/scripts/dev_start.sh")

    def move_file(self, source_dir, target_dir):
        if os.path.exists(target_dir):
            os.remove(target_dir)
        shutil.copy(source_dir, target_dir)

    def change_map_file(self):
        with open(FLAGFILE_PATH, "a") as f:
            f.write(f"\n--map_dir=/apollo/modules/map/data/{MAP_NAME}\n")

    def move_scripts(self):
        if not os.path.exists(f"{MY_SCRIPTS_DIR}"):
            os.mkdir(f"{MY_SCRIPTS_DIR}")
        for file_name in os.listdir(f"{PROJECT_ROOT}/data/scripts"):
            if ".sh" in file_name:
                self.move_file(f"{PROJECT_ROOT}/data/scripts/{file_name}", f"{MY_SCRIPTS_DIR}/{file_name}")

    def move_dir(self, source_dir, target_dir):
        if not os.path.exists(target_dir):
            shutil.copytree(source_dir, target_dir)

    def delete_dir(self, dir_path, mk_dir):
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        if mk_dir:
            os.makedirs(dir_path)
