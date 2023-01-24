import math
from copy import deepcopy
from range_analysis.OptionTuningItem import OptionTuningItem


class RangeAnalyzer:
    def __init__(self, config_file_obj):
        self.range_list = self.range_init(config_file_obj.option_type_list)
        self.original_range_list = deepcopy(self.range_list)

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
