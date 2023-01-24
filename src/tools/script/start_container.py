from config import OPT_MODE, APOLLO_ROOT, CONTAINER_NUM
from environment.Container import Container
from environment.MapLoader import MapLoader

if __name__ == '__main__':
    containers = [Container(APOLLO_ROOT, f'ROUTE_{x}') for x in range(1)]
    map_instance = MapLoader().map_instance

    for ctn in containers:
        ctn.start_instance()

        ctn.restart_dreamview()

        ctn.connect_bridge()
        ctn.create_message_handler(map_instance)
        ctn.message_handler.send_initial_localization()
        ctn.start_sim_control_standalone()

        print(f'Dreamview at http://{ctn.ip}:{ctn.port}')

