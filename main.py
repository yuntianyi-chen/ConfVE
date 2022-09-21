from tools.config_file_handler.parser_apollo import processed_parser
from tools.config_file_handler.translator_apollo import translator, save2file

if __name__ == '__main__':
    # stack, option_num = raw_parser("./configuration_files/Apollo/planning_config.pb.txt")
    raw_option_stack, option_tuple_list, option_num = processed_parser(
        "./configuration_files/Apollo/test_planning_config.pb.txt")
    output_string_list = translator(option_tuple_list)
    save2file(output_string_list)