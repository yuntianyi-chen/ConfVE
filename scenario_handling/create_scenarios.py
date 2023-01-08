import os
import shutil
import signal
import glob
import subprocess
import time
from config import APOLLO_ROOT, MODULE_NAME, MAGGIE_ROOT, DEFAULT_CONFIG_FILE, TRAFFIC_LIGHT_MODE
from environment.container_settings import get_container_name
from scenario_handling.traffic_light_control.traffic_light_control import TCSection
from tools.config_file_handler.translator_apollo import option_obj_translator, save2file


class Scenario:

    def __init__(self, obs_group_path, adc_route, record_name):
        self.obs_group_path = obs_group_path
        self.adc_route = adc_route
        self.record_name = record_name

        if TRAFFIC_LIGHT_MODE:
            self.traffic_light_control = TCSection.get_one()
        # self.tm =

    def update_config_file_status(self, config_file_status):
        self.config_file_status = config_file_status

    def update_routing_perception_info(self, obs_perception_messages, routing_request_message):
        self.obs_perception_messages = obs_perception_messages
        self.routing_request_message = routing_request_message

    def update_original_violations(self, violation_num, violation_results):
        self.original_violation_num = violation_num
        self.original_violation_results = violation_results

    def start_recorder(self):
        time.sleep(0.5)
        cmd = f"docker exec -d {get_container_name()} /apollo/bazel-bin/cyber/tools/cyber_recorder/cyber_recorder record -o /apollo/records/{self.record_name} -a &"
        recorder_subprocess = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        return recorder_subprocess

    def stop_recorder(self, recorder_subprocess):
        cmd = f"docker exec -d {get_container_name()} /apollo/scripts/my_scripts/stop_recorder.sh"
        subprocess.run(cmd.split())
        self.delete_recorder_log()
        time.sleep(0.5)

    def delete_record(self):
        os.remove(f"{APOLLO_ROOT}/records/{self.record_name}.00000")

    def stop_subprocess(self, p):
        try:
            os.kill(p.pid, signal.SIGINT)
            p.kill()
        except OSError:
            print("stopped")

    def delete_recorder_log(self):
        files = glob.glob(f'{APOLLO_ROOT}/cyber_recorder.log.INFO.*')
        for file in files:
            os.remove(file)


def config_file_generating(generated_individual, option_obj_list, default):
    if default:
        shutil.copy(f"{MAGGIE_ROOT}/backup/config files/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt",
                    f"{APOLLO_ROOT}/modules/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt")
    else:
        generated_value_list = generated_individual.value_list
        for generated_value, option_obj in zip(generated_value_list, option_obj_list):
            option_obj.option_value = generated_value
        output_string_list = option_obj_translator(option_obj_list)
        save2file(output_string_list)
        config_file_tuned_status = True  # config file tuned
        return config_file_tuned_status


# scenario refers to different config settings with fixed obstacles and adc routing
def create_scenarios(generated_individual, option_obj_list, gen_ind_id, pre_record_info):
    config_file_tuned_status = config_file_generating(generated_individual, option_obj_list,
                                                      default=DEFAULT_CONFIG_FILE)
    record_name_list = [f"{gen_ind_id}_Scenario_{str(i)}" for i in range(len(pre_record_info.adc_routing_list))]

    # tm = TrafficControlManager(self.curr_scenario.tc_section)

    scenario_list = []
    for i in range(len(record_name_list)):
        scenario = Scenario(pre_record_info.obs_group_path_list[i], pre_record_info.adc_routing_list[i],
                            record_name_list[i])
        scenario.update_config_file_status(config_file_tuned_status)
        scenario.update_original_violations(pre_record_info.violation_num_list[i],
                                            pre_record_info.violation_results_list[i])
        scenario.update_routing_perception_info(pre_record_info.obs_perception_list[i],
                                                pre_record_info.routing_request_list[i])
        scenario_list.append(scenario)
    return scenario_list
