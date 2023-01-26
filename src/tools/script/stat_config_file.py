import os
from config import DEFAULT_CONFIG_FILE_PATH, PROJECT_ROOT, MODULE_NAME, CONFIG_FILE_NAME
from config_file_handler.parser_apollo import config_file_parser2obj

if __name__ == '__main__':
    # print(os.getcwd())
    # os.chdir(PROJECT_ROOT)
    # module_config_path = f"{APOLLO_ROOT}/modules/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
    # module_config_path = f"../data/config_files/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
    # module_name = "control"

    # conf_files_path = glob.glob(
    #     f"C:\\Projects\\Research\\Autonomous Vehicles\\apollo\\apollo\\modules\\{module_name}\\conf" + '/**/calibration_table.pb.txt',
    #     recursive=True)

    conf_files_path = [f"{CONFIG_FILE_NAME}"]

    all_config_files_path = conf_files_path
    type_stat_dict = {}
    print(len(all_config_files_path))
    for config_file in all_config_files_path:
        # if "calibration" in config_file:
        # ga_main(module_config_path)
        print(config_file)
        # raw_option_stack, option_tuple_list, option_obj_list, option_num = parser2class(config_file)

        # init_individual_list, generation_limit, option_type_list = ga_init(option_obj_list)
        config_file_obj = config_file_parser2obj(config_file)

        for i in config_file_obj.option_type_list:
            if i not in type_stat_dict.keys():
                type_stat_dict[i] = 1
            else:
                type_stat_dict[i] += 1

    print(type_stat_dict)
    print(sum(type_stat_dict.values()))