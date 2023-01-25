import os
import shutil
from config import OPT_MODE, APOLLO_ROOT, CONTAINER_NUM, MY_SCRIPTS_DIR, PROJECT_ROOT, FLAGFILE_PATH, MAP_NAME
from environment.Container import Container
from environment.MapLoader import MapLoader
from optimization_algorithms.genetic_algorithm.GARunner import GARunner


def move_scripts():
    target_scripts_dir = MY_SCRIPTS_DIR
    if not os.path.exists(target_scripts_dir):
        source_scripts_dir = f"{PROJECT_ROOT}/data/scripts"
        shutil.copytree(source_scripts_dir, target_scripts_dir)


def change_map_file():
    with open(FLAGFILE_PATH, "a") as f:
        f.write(f"\n--map_dir=/apollo/modules/map/data/{MAP_NAME}\n")


if __name__ == '__main__':
    move_scripts()
    change_map_file()
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
