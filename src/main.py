from config import OPT_MODE, APOLLO_ROOT, CONTAINER_NUM
from environment.Container import Container
from optimization_algorithms.genetic_algorithm.GARunner import GARunner

if __name__ == '__main__':
    containers = [Container(APOLLO_ROOT, f'ROUTE_{x}') for x in range(CONTAINER_NUM)]


    for ctn in containers:
        ctn.start_instance()
        # ctn.stop_modules()

        ctn.cyber_env_init()

        # ctn.modules_operation(operation="stop")
        # ctn.close_subprocess()
        # ctn.start_dreamview()
        # ctn.dreamview.start_sim_control()
        # ctn.modules_operation(operation="start")

        ctn.connect_bridge()
        ctn.create_message_handler()
        print(f'Dreamview at http://{ctn.ip}:{ctn.port}')


    if OPT_MODE == "GA":
        GARunner(containers)
