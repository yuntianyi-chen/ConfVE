import os
import re
import glob
# import numpy as np
# import pandas as pd
from copy import deepcopy

from tools.script.config_file_handler.translator_apollo import option_obj_translator, save2file


# from tools.config_file_handler.translator_apollo import option_obj_translator, save2file


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


def raw_parser(config_file_path):
    # config_txt_file = open("./configuration_files/Apollo/planning_config.pb.txt", "r")
    config_txt_file = open(config_file_path, "r")
    # data = config_txt_file.read()
    lines = config_txt_file.readlines()
    config_txt_file.close()
    stack = list()
    option_count = 0
    for line in lines:
        # Use stack to store the structure
        # 'xxx {' or 'xxx: {'
        pattern1 = re.compile(r"^\s*(\w+)\s*:?\s*{\s*\n$")
        match1 = pattern1.match(line)
        if match1:
            key = match1.group(1)
            # print("P1 " + key)
            stack.append(key)
        else:
            # option key-value
            # 'xxx: xxx'
            pattern2 = re.compile(r"^\s*(\w+):\s*(.+)\s*\n$")
            match2 = pattern2.match(line)
            if match2:
                key = match2.group(1)
                value = match2.group(2)
                # print("P2 " + key + " " + value)
                stack.append((key, value))
                option_count += 1
            else:
                # '}'
                pattern3 = re.compile(r"^\s*}\s*\n$")
                match3 = pattern3.match(line)
                if match3:
                    # print("P3 }")
                    value_list = []
                    while True:
                        item = stack.pop()
                        if type(item) is tuple:
                            value_list.append(item)
                        else:
                            value_list.reverse()
                            stack.append((item, value_list))
                            break
    return stack, option_count


# option tuple: (option_id, option_key, option_value, option_type, position, layers)
def parser2tuple(config_file_path):
    # config_txt_file = open("./configuration_files/Apollo/planning_config.pb.txt", "r")
    config_txt_file = open(config_file_path, "r")
    # data = config_txt_file.read()
    lines = config_txt_file.readlines()
    # lines = ["xxx {\n"]+lines+["}\n"]
    config_txt_file.close()
    raw_option_stack = list()
    option_count = 0
    position_id = 0
    # sub_position_id = 0
    # layer = 0
    position_stack = list()
    option_tuple_list = list()
    layer_stack = list()
    for line in lines:
        # Use stack to store the structure
        # 'xxx {' or 'xxx: {'
        pattern1 = re.compile(r"^\s*(\w+)\s*:?\s*{\s*\n$")
        match1 = pattern1.match(line)
        if match1:
            position_stack.append(position_id)
            # layer += 1
            position_id = 0
            key = match1.group(1)
            raw_option_stack.append(key)
            layer_stack.append(key)
        else:
            # option key-value
            # 'xxx: xxx'
            pattern2 = re.compile(r"^\s*(\w+):\s*(.+)\s*\n$")
            match2 = pattern2.match(line)
            if match2:
                key = match2.group(1)
                value = match2.group(2)
                item = (key, value)
                option_count += 1
                option_id = option_count - 1
                position_stack.append(position_id)
                option_processed_tuple = (option_id,) + item + (
                    analyze_type(item[1]), deepcopy(position_stack), deepcopy(layer_stack))
                raw_option_stack.append(option_processed_tuple)
                option_tuple_list.append(option_processed_tuple)
                position_stack.pop()
                position_id += 1
            else:
                # '}'
                pattern3 = re.compile(r"^\s*}\s*\n$")
                match3 = pattern3.match(line)
                if match3:
                    item_list = []

                    while True:
                        item = raw_option_stack.pop()
                        if type(item) is tuple:
                            item_list.append(item)
                        else:
                            item_list.reverse()
                            # layer_stack.pop()
                            raw_option_stack.append((item, item_list))
                            position_id = position_stack.pop() + 1
                            break
                # else:
                #     # '# xxx'
                #     pattern4 = re.compile(r"^\s*#.*\n$")
                #     match4 = pattern4.match(line)
                #     if match4:
                #         print("P4 #")
                #     else:
                #         print("P5")
    return raw_option_stack, option_tuple_list, option_count
    # return option_tuple_list, option_count


# option item class: (option_id, option_key, option_value, option_type, position, layers)

class OptionObj:
    def __init__(self, option_id, option_key, option_value, option_type, position, layers):
        self.option_id = option_id
        self.option_key = option_key
        self.option_value = option_value
        self.option_type = option_type
        self.position = position
        self.layers = layers


def parser2class(config_file_path):
    config_txt_file = open(config_file_path, "r")
    lines = config_txt_file.readlines()
    config_txt_file.close()
    option_count = 0
    position_id = 0
    position_stack = list()
    raw_option_stack = list()
    option_tuple_list = list()
    option_obj_list = list()

    layer_stack = list()
    for line in lines:
        # Use stack to store the structure
        # 'xxx {' or 'xxx: {'
        pattern1 = re.compile(r"^\s*(\w+)\s*:?\s*{\s*\n$")
        match1 = pattern1.match(line)
        if match1:
            position_stack.append(position_id)
            position_id = 0
            layer_key = match1.group(1)
            raw_option_stack.append(layer_key)
            layer_stack.append(layer_key)
        else:
            # option key-value
            # 'xxx: xxx'
            pattern2 = re.compile(r"^\s*(\w+):\s*(.+)\s*\n$")
            match2 = pattern2.match(line)
            if match2:
                option_key = match2.group(1)
                option_value = match2.group(2)
                # item = (key, value)
                option_count += 1
                option_id = option_count - 1
                position_stack.append(position_id)
                option_obj = OptionObj(option_id, option_key, option_value, analyze_type(option_value),
                                       deepcopy(position_stack), deepcopy(layer_stack))
                option_processed_tuple = (option_id,) + (option_key, option_value, analyze_type(option_value),
                                                         deepcopy(position_stack), deepcopy(layer_stack))
                raw_option_stack.append(option_processed_tuple)
                option_tuple_list.append(option_processed_tuple)
                option_obj_list.append(option_obj)
                position_stack.pop()
                position_id += 1
            else:
                # '}'
                pattern3 = re.compile(r"^\s*}\s*\n$")
                match3 = pattern3.match(line)
                if match3:
                    item_list = []
                    while True:
                        item = raw_option_stack.pop()
                        if type(item) is tuple:
                            item_list.append(item)
                        else:
                            item_list.reverse()
                            layer_stack.pop()
                            # current_layer = layer_stack.pop()
                            raw_option_stack.append((item, item_list))
                            position_id = position_stack.pop() + 1
                            break
                # else:
                #     # '# xxx'
                #     pattern4 = re.compile(r"^\s*#.*\n$")
                #     match4 = pattern4.match(line)
                #     if match4:
                #         print("P4 #")
                #     else:
                #         print("P5")
    return raw_option_stack, option_tuple_list, option_obj_list, option_count
    # return option_obj_list, option_count


def analyze_type(value):
    # value_type = None
    if value == 'false' or value == 'true':
        value_type = "boolean"
    elif re.fullmatch(r"-?\d+(\.\d+)", value):
        value_type = "float"
    elif re.fullmatch(r"-?\d+(\d*)", value):
        value_type = "integer"
    elif re.fullmatch(r"-?\d+((\.\d+)|(\d*))e\d+(\d*)", value):
        value_type = "e_number"
    else:
        value_type = "string"
    # value_type = type(value)
    return value_type


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
