from config import MODULE_NAME, APOLLO_ROOT, MAGGIE_ROOT
from environment.container_settings import init_settings
from optimization_algorithms.ga_main import ga_main


def select_module():
    module_config_path = f"{MAGGIE_ROOT}/data/config_files/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
    return module_config_path


if __name__ == '__main__':
    init_settings()
    module_config_path = select_module()
    ga_main(module_config_path)
