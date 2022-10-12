import os
import random
import shutil
import signal
import glob
import subprocess
import time
from config import APOLLO_ROOT, MAP_NAME, MODULE_NAME, MAGGIE_ROOT, DEFAULT_CONFIG_FILE
from environment.container_settings import get_container_name
from scenario_handling.scenario_tools import map_tools
from scenario_handling.scenario_tools.map_info_parser import validatePath, initialize
from tools.config_file_handler.translator_apollo import option_obj_translator, save2file


class Scenario:
    def __init__(self, config_file_status, obs_group_path, adc_route, record_name):
        self.config_file_status = config_file_status
        self.obs_group_path = obs_group_path
        self.adc_route = adc_route
        self.record_name = record_name

    def start_recorder(self):
        cmd = f"docker exec -d {get_container_name()} /apollo/bazel-bin/cyber/tools/cyber_recorder/cyber_recorder record -o /apollo/records/{self.record_name} -a &"
        recorder_subprocess = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return recorder_subprocess

    def stop_recorder(self, recorder_subprocess):
        cmd = f"docker exec -d {get_container_name()} /apollo/scripts/my_scripts/stop_recorder.sh"
        subprocess.run(cmd.split())
        time.sleep(1)
        self.delete_recorder_log()

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

    def calculate_fitness(self, violation_number, code_coverage, execution_time):
        self.violation_number = violation_number
        self.code_coverage = code_coverage
        self.execution_time = execution_time
        self.fitness = violation_number * code_coverage * execution_time

    def get_fitness(self):
        return self.fitness


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


def read_obstacles():
    obs_folder = f"{APOLLO_ROOT}/modules/tools/perception/obstacles/{MAP_NAME}/"
    obs_apollo_folder = f"{MAP_NAME}/"
    obs_group_folders_name_list = os.listdir(obs_folder)
    obs_group_folders_name_list.sort()
    obs_group_path_list = []
    for obs_group_folder_name in obs_group_folders_name_list:
        obs_group_path_list.append(obs_apollo_folder + obs_group_folder_name)
    return obs_group_path_list




def adc_routing_generate():
    # this function costs calculating resources
    ptl_dict, ltp_dict, diGraph = initialize()

    valid_path = False
    while not valid_path:
        p_index1 = random.randint(0, len(ptl_dict.keys()) - 1)
        p_index2 = random.randint(0, len(ptl_dict.keys()) - 1)
        start_point = tuple(map(float, list(ptl_dict.keys())[p_index1].split('-')))
        if not map_tools.all_points_not_in_junctions(start_point):
            p1 = list(ptl_dict.keys())[p_index1]
            p2 = list(ptl_dict.keys())[p_index2]
            continue
        valid_path = validatePath(p_index1, p_index2, ptl_dict, ltp_dict, diGraph)
    p1 = list(ptl_dict.keys())[p_index1]
    p2 = list(ptl_dict.keys())[p_index2]
    adc_routing = p1.replace('-', ',') + "," + p2.replace('-', ',')
    return adc_routing


# scenario refers to different config settings with fixed obstacles and adc routing
def create_scenarios(generated_individual, option_obj_list, generation_num, individual_num):
    config_file_tuned_status = config_file_generating(generated_individual, option_obj_list,
                                                      default=DEFAULT_CONFIG_FILE)
    obs_group_path_list = read_obstacles()
    # adc_routing = adc_routing_generate()
    # adc_routing_list = ["586980.86,4140959.45,587283.52,4140882.30" for i in obs_group_path_list]
    adc_routing_list = [adc_routing_generate() for i in obs_group_path_list]
    record_name_list = [f"Generation_{str(generation_num)}_Config_{individual_num}_Obs_{str(i)}" for i in
                        range(len(adc_routing_list))]
    scenario_list = [Scenario(config_file_tuned_status, obs_group_path, adc_route, record_name) for
                     obs_group_path, adc_route, record_name in
                     zip(obs_group_path_list, adc_routing_list, record_name_list)]

    return scenario_list


if __name__ == "__main__":
    adc_routing = adc_routing_generate()
    adc_route_raw = adc_routing.split(',')
    init_x, init_y, dest_x, dest_y = float(adc_route_raw[0]), float(adc_route_raw[1]), float(
        adc_route_raw[2]), float(adc_route_raw[3])

    print()
