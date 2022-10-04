from config import MODULE_NAME, APOLLO_ROOT
from optimization_algorithms.ga_main import ga_main


def select_module():
    # module_selected = MODULE_NAME
    # module_config_path = "./configuration_files/Apollo/test_planning_config.pb.txt"
    module_config_path = f"{APOLLO_ROOT}/modules/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
    return module_config_path


if __name__ == '__main__':
    # init_settings()
    module_config_path = select_module()
    ga_main(module_config_path)
