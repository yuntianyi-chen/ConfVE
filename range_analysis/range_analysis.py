import random

def generate_new_range(cur_range, option_tuning_item, default_option_value_list):
    cur_lower_bound = cur_range[0]
    cur_upper_bound = cur_range[1]
    default_option_value = default_option_value_list[option_tuning_item.position]
    cur_option_value = option_tuning_item.cur_value

    if default_option_value > cur_option_value:
        new_range = [cur_option_value, cur_upper_bound]
    elif default_option_value < cur_option_value:
        new_range = [cur_lower_bound, cur_option_value]
    else:
        new_range = cur_range
    return new_range


def range_init(option_obj_list):
    range_list = list()
    for option_obj in option_obj_list:
        option_type = option_obj.option_type
        option_value = option_obj.option_value
        option_range = generate_option_range(option_type, option_value)
        if option_range:
            range_list.append(option_range)
        else:
            # range_list.append(None)
            range_list.append([])
    return range_list


def generate_option_range(option_type, option_value):
    # initial range should contain default option value
    if option_type == "float":
        option_range = [-10001, 10001]
    elif option_type == "integer":
        option_range = [-10001, 10001]
    elif option_type == "boolean":
        option_range = ["true", "false"]
    elif option_type == "string":
        option_range = []
    elif option_type == "e_number":
        option_range = []
    else:
        option_range = []

    return option_range
