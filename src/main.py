import os
import shutil
from config import OPT_MODE, APOLLO_ROOT, CONTAINER_NUM, MY_SCRIPTS_DIR, PROJECT_ROOT
from environment.Container import Container
from environment.MapLoader import MapLoader
from optimization_algorithms.genetic_algorithm.GARunner import GARunner


def move_scripts():
    target_scripts_dir = MY_SCRIPTS_DIR
    if not os.path.exists(target_scripts_dir):
        source_scripts_dir = f"{PROJECT_ROOT}/data/scripts"
        shutil.copytree(source_scripts_dir, target_scripts_dir)

if __name__ == '__main__':
    move_scripts()
    containers = [Container(APOLLO_ROOT, f'ROUTE_{x}') for x in range(CONTAINER_NUM)]
    map_instance = MapLoader().map_instance

    for ctn in containers:
        ctn.start_instance()
        ctn.restart_dreamview()
        ctn.connect_bridge()
        ctn.create_message_handler(map_instance)
        # ctn.message_handler.send_initial_localization()
        # ctn.start_sim_control_standalone()

        print(f'Dreamview at http://{ctn.ip}:{ctn.port}')

    if OPT_MODE == "GA":
        GARunner(containers)



