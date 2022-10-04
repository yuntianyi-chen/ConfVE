from optimization_algorithms.ga_main import ga_main


def select_module():
    module_selected = "planning"
    module_config_path = "./configuration_files/Apollo/test_planning_config.pb.txt"
    return module_config_path


if __name__ == '__main__':
    # init_settings()

    module_config_path = select_module()

    ga_main(module_config_path)
