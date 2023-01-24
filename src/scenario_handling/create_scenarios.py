import shutil
import time
from copy import deepcopy
from config import DEFAULT_CONFIG_FILE, TRAFFIC_LIGHT_MODE, AV_TESTING_APPROACH, DEFAULT_CONFIG_FILE_PATH, \
    CURRENT_CONFIG_FILE_PATH
from config_file_handler.translator_apollo import option_obj_translator, save2file
from scenario_handling.Scenario import Scenario
from tools.traffic_light_control.traffic_light_control import TCSection


def config_file_generating(generated_individual, config_file_obj, default):
    new_option_obj_list = deepcopy(config_file_obj.option_obj_list)
    if default:
        shutil.copy(DEFAULT_CONFIG_FILE_PATH, CURRENT_CONFIG_FILE_PATH)
    else:
        generated_value_list = generated_individual.value_list
        for generated_value, option_obj in zip(generated_value_list, new_option_obj_list):
            option_obj.option_value = generated_value
        output_string_list = option_obj_translator(new_option_obj_list)
        save2file(output_string_list)
        config_file_tuned_status = True  # config file tuned
        return config_file_tuned_status


# scenario refers to different config settings with fixed obstacles and adc routing
def create_scenarios(generated_individual, config_file_obj, pre_record_info_list, containers, name_prefix):
    config_file_tuned_status = config_file_generating(generated_individual, config_file_obj,
                                                      default=DEFAULT_CONFIG_FILE)

    # print("Restart Modules...")
    # for container in containers:
    #     container.restart_modules()
    # time.sleep(2)

    scenario_list = []
    for pre_record_info in pre_record_info_list:
        record_name = f"{name_prefix}_Scenario_{str(pre_record_info.record_id)}"

        scenario = Scenario(record_name, pre_record_info.record_id)

        scenario.update_config_file_status(config_file_tuned_status)
        if AV_TESTING_APPROACH != "Random":

            scenario.update_record_info(pre_record_info)

            if TRAFFIC_LIGHT_MODE == "read":
                traffic_light_control = pre_record_info.traffic_lights_list
            elif TRAFFIC_LIGHT_MODE == "random":
                traffic_light_control = TCSection.get_one()
            else:
                traffic_light_control = None
            scenario.update_traffic_lights(traffic_light_control)
        scenario_list.append(scenario)
    return scenario_list
