import os
import shutil
import warnings
from config import OPT_MODE, APOLLO_ROOT, CONTAINER_NUM, MY_SCRIPTS_DIR, PROJECT_ROOT, FLAGFILE_PATH, MAP_NAME, \
    DEFAULT_CONFIG_FILE_PATH, CURRENT_CONFIG_FILE_PATH, APOLLO_MAP_DATA_DIR, MAP_DIR
from environment.Container import Container
from environment.MapLoader import MapLoader
from optimization_algorithms.baseline.TwayRunner import TwayRunner
from optimization_algorithms.genetic_algorithm.GARunner import GARunner


warnings.filterwarnings('ignore')

def move_default_config_file():
    if os.path.exists(CURRENT_CONFIG_FILE_PATH):
        os.remove(CURRENT_CONFIG_FILE_PATH)
    shutil.copy(DEFAULT_CONFIG_FILE_PATH, CURRENT_CONFIG_FILE_PATH)


def change_map_file():
    with open(FLAGFILE_PATH, "a") as f:
        f.write(f"\n--map_dir=/apollo/modules/map/data/{MAP_NAME}\n")


def move_data(source_dir, target_dir):
    if not os.path.exists(target_dir):
        shutil.copytree(source_dir, target_dir)


if __name__ == '__main__':
    move_data(MAP_DIR, f"{APOLLO_MAP_DATA_DIR}/{MAP_NAME}")
    move_data(f"{PROJECT_ROOT}/data/scripts", MY_SCRIPTS_DIR)

    # move_scripts()
    change_map_file()
    move_default_config_file()

    containers = [Container(APOLLO_ROOT, f'ROUTE_{x}') for x in range(CONTAINER_NUM)]
    map_instance = MapLoader().map_instance

    for ctn in containers:
        ctn.start_instance()
        ctn.cyber_env_init()
        ctn.connect_bridge()
        ctn.create_message_handler(map_instance)

        print(f'Dreamview at http://{ctn.ip}:{ctn.port}')

    if OPT_MODE == "GA":
        GARunner(containers)
    elif OPT_MODE == "T-way":
        TwayRunner(containers)
