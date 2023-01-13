import glob

from config_file_handler.parser_apollo import raw_parser


def analyze_all_modules():
    conf_files_path = glob.glob(
        "C:\\Projects\\Research\\Autonomous Vehicles\\apollo\\apollo\\modules" + '/**/*_conf.pb.txt',
        recursive=True)
    config_files_path = glob.glob(
        "C:\\Projects\\Research\\Autonomous Vehicles\\apollo\\apollo\\modules" + '/**/*_config.pb.txt',
        recursive=True)
    all_config_files_path = conf_files_path + config_files_path
    pd_rows = []
    for config_file_path in all_config_files_path:
        stack, option_num = raw_parser(config_file_path)
        # print(option_num)
        module_name = config_file_path.split('modules')[1].split('\\')[1]
        file_name = config_file_path.split('\\')[-1]

        # value_entry = list(arg_item.attrib.values())
        # value_entry.append(judge_arg_type(value_entry[1]))
        pd_rows.append([module_name, file_name, config_file_path, option_num])
        # print()

    # rows_df = pd.DataFrame(np.array(pd_rows), columns=['module_name', 'file_name', 'file_path', 'option_number'])
    # rows_df.to_csv('apollo_config_files.csv', index=False)



if __name__ == '__main__':
    working_dir_path = "C:/Users/cloud/PycharmProjects/AV_Testing"
    os.chdir(working_dir_path)
    # stack, option_num = raw_parser("./configuration_files/Apollo/planning_config.pb.txt")
    # raw_option_stack, option_tuple_list, option_num = parser2tuple(
    #     "./configuration_files/Apollo/test_planning_config.pb.txt")
    raw_option_stack, option_tuple_list, option_obj_list, option_num = parser2class(
        "./configuration_files/Apollo/test_planning_config.pb.txt")
    output_string_list = option_obj_translator(option_obj_list)
    save2file(output_string_list)
