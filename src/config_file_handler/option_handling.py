import random
from copy import deepcopy
from range_analysis.OptionTuningItem import OptionTuningItem


def tune_one_value(individual_obj, config_file_obj, range_analyzer, position):
    option_type = config_file_obj.option_type_list[position]

    if option_type in ["float", "integer", "boolean", "e_number"]:
        option_value = individual_obj.value_list[position]
        individual_obj.pre_value_list = deepcopy(individual_obj.value_list)

        generated_value = generate_option_value_from_range(option_type, option_value,
                                                           range_analyzer.range_list[position])

        individual_obj.value_list[position] = generated_value

        individual_obj.option_tuning_tracking_list.append(
            OptionTuningItem(position, option_type, config_file_obj.option_obj_list[position].option_key,
                             individual_obj.pre_value_list[position],
                             individual_obj.value_list[position], config_file_obj.option_obj_list[position]))
        return True
    else:
        return False


def generate_option_value_from_range(option_type, option_value, option_range):
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
        generated_value = option_value
    elif option_type == "enum":
        generated_value = option_value
    else:
        generated_value = option_value

    return str(generated_value)
