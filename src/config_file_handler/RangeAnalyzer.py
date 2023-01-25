import re
import math
import random
from copy import deepcopy
from config_file_handler.OptionTuningItem import OptionTuningItem
from config_file_handler.mit_operator import MisInjTester


class RangeAnalyzer:
    def __init__(self, config_file_obj):
        self.range_list = self.range_init(config_file_obj.option_type_list)
        self.original_range_list = deepcopy(self.range_list)
        self.mit_inj_tester = MisInjTester()

    def generate_new_range(self, cur_range, option_tuning_item, config_file_obj):
        cur_lower_bound = cur_range[0]
        cur_upper_bound = cur_range[1]

        default_option_value = config_file_obj.default_option_value_list[option_tuning_item.position]
        cur_option_value = option_tuning_item.cur_value

        if option_tuning_item.option_type == "e_number":
            default_exp_raw = default_option_value.split("e")[-1]
            if default_exp_raw[0:2] == "-0":
                default_exp = int(default_exp_raw[2:])
            elif default_exp_raw[0] == "0":
                default_exp = int(default_exp_raw[1:])
            else:
                default_exp = int(default_exp_raw)

            cur_exp = int(cur_option_value.split("e")[-1])

            if default_exp > cur_exp:
                new_range = [cur_exp, cur_upper_bound]
            elif default_exp < cur_exp:
                new_range = [cur_lower_bound, cur_exp]
            else:
                new_range = cur_range
        elif option_tuning_item.option_type == "boolean":
            new_range = cur_range
        else:
            default_value = eval(default_option_value)
            cur_value = eval(cur_option_value)
            if default_value > cur_value:
                new_range = [math.ceil(cur_value), cur_upper_bound]
            elif default_value < cur_value:
                new_range = [cur_lower_bound, math.floor(cur_value)]
            else:
                new_range = cur_range
        return new_range

    def range_init(self, option_type_list):
        range_list = list()
        for option_type in option_type_list:
            option_range = self.generate_option_range(option_type)
            if option_range:
                range_list.append(option_range)
            else:
                range_list.append([])
        return range_list

    def generate_option_range(self, option_type):
        # initial range should contain default option value
        if option_type == "float":
            option_range = [-10001, 10001]
        elif option_type == "integer":
            option_range = [-10001, 10001]
        elif option_type == "boolean":
            option_range = ["true", "false"]
        elif option_type == "e_number":
            option_range = [-101, 101]  # e.g., [1e-100, 1e100]
        elif option_type == "string":
            option_range = []
        elif option_type == "enum":
            option_range = []
        else:
            option_range = []
        return option_range

    def range_analyze(self, option_tuning_item, config_file_obj):
        range_change_str = "  Range Change: default\n"
        if isinstance(option_tuning_item, OptionTuningItem):
            cur_range = self.range_list[option_tuning_item.position]
            new_range = self.generate_new_range(cur_range, option_tuning_item, config_file_obj)
            self.range_list[option_tuning_item.position] = new_range
            range_change_str = f"  Range Change: {option_tuning_item.position}, {option_tuning_item.option_key}, {cur_range}->{new_range}\n"
        return range_change_str

    def tune_one_value(self, individual_obj, config_file_obj, position):
        option_type = config_file_obj.option_type_list[position]

        # if option_type in ["float", "integer", "boolean", "e_number"]:
        option_value = individual_obj.value_list[position]
        individual_obj.pre_value_list = deepcopy(individual_obj.value_list)

        generated_value = self.generate_new_option_value(option_type, option_value, self.range_list[position])

        individual_obj.value_list[position] = generated_value
        individual_obj.option_tuning_tracking_list.append(
            OptionTuningItem(position, option_type, config_file_obj.option_obj_list[position].option_key,
                             individual_obj.pre_value_list[position], individual_obj.value_list[position],
                             config_file_obj.option_obj_list[position]))
        #     return True
        # else:
        #     return False

    def generate_new_option_value(self, option_type, option_value, option_range):
        if option_type == "float":
            round_bit = len(option_value.split(".")[1])
            generated_value = round(random.uniform(option_range[0], option_range[1]), round_bit)
        elif option_type == "integer":
            generated_value = random.randint(option_range[0], option_range[1])
        elif option_type == "boolean":
            generated_value = "true" if option_value == "false" else "false"
        elif option_type == "e_number":
            exp = random.randint(option_range[0], option_range[1])
            forward = option_value.split("e")[0]
            generated_value = f"{forward}e{exp}"
        elif option_type == "string":
            if option_value in ["min", "max"]:
                generated_value = "min" if option_value == "max" else "min"
            elif option_value in ["yes", "no"]:
                generated_value = "yes" if option_value == "no" else "min"
            else:
                generated_value = self.mit_inj_tester.apply_one_operator(option_value)
        elif option_type == "enum":
            generated_value = self.mit_inj_tester.apply_one_operator(option_value)
        else:
            generated_value = option_value
        return str(generated_value)

def analyze_type(value):
    if value == 'false' or value == 'true':
        value_type = "boolean"
    elif re.fullmatch(r"-?\d+(\.\d+)", value):
        value_type = "float"
    elif re.fullmatch(r"-?\d+(\d*)", value):
        value_type = "integer"
    elif re.fullmatch(r"-?\d+((\.\d+)|(\d*))e\d+(\d*)", value):
        value_type = "e_number"
    elif re.fullmatch(r"\".*\"", value):
        value_type = "string"
    else:
        value_type = "enum"
    return value_type