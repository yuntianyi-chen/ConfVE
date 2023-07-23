import warnings
from config import OPT_MODE, APOLLO_ROOT, CONTAINER_NUM
from environment.Container import Container
from environment.InitRunner import InitRunner
from environment.MapLoader import MapLoader
from optimization_algorithms.baseline.OneEnabledRunner import OneEnabledRunner
from optimization_algorithms.baseline.TwayRunner import TwayRunner
from optimization_algorithms.genetic_algorithm.GARunner import GARunner
from range_analysis.PreAnalyzeRunner import PreAnalyzeRunner

warnings.filterwarnings('ignore')


def confve_main():
    InitRunner()

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
    elif OPT_MODE == "OneEnabled":
        OneEnabledRunner(containers)
    elif OPT_MODE == "PreAnalyze":
        PreAnalyzeRunner(containers)


if __name__ == '__main__':
    confve_main()
