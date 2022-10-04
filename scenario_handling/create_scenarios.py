import os
import random
import shutil
import subprocess

from config import APOLLO_ROOT, MAP_NAME, MODULE_NAME, MAGGIE_ROOT
from environment.container_settings import get_container_name
from run_scenarios.auxiliary.map import map_tools
from scenario_handling.scenario_tools.map_info_parser import validatePath, initialize
from tools.config_file_handler.translator_apollo import option_obj_translator, save2file


class Scenario:
    def __init__(self, config_file_status, obs_group_path, adc_route, record_name):
        self.config_file_status = config_file_status
        self.obs_group_path = obs_group_path
        self.adc_route = adc_route
        self.record_name = record_name

    def start_recorder(self):
        # cmd = f"docker exec -d {get_container_name()} cyber_recorder record -o {RECORDS_DIR}/{self.record_name} -a &"

        cmd = f"docker exec -d {get_container_name()} cyber_recorder record -o /apollo/records/{self.record_name} -a &"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop_recorder(self):
        cmd = f"docker exec -d {get_container_name()} python3 /apollo/scripts/record_bag.py --stop --stop_signal SIGINT > /dev/null 2>&1"
        subprocess.run(cmd.split())


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
    obs_apollo_folder = f"/apollo/modules/tools/perception/obstacles/{MAP_NAME}/"
    # pop_pickle_dump_data_path = f"{APOLLO_ROOT}/modules/tools/perception/pop_pickle/{MAP_NAME}_dump_data"
    # pop_pickle_dump_data_file = open(pop_pickle_dump_data_path, "rb")
    # pop = pickle.load(pop_pickle_dump_data_file)
    # obs_group_num = 0
    obs_group_folders_name_list = os.listdir(obs_folder)
    obs_group_folders_name_list.sort()
    obs_group_path_list = []
    for obs_group_folder_name in obs_group_folders_name_list:
        obs_group_path_list.append(obs_apollo_folder + obs_group_folder_name)

        # obs_files_name_list = os.listdir(obs_folder + obs_group_folder_name)
        # start_time = time.time()
        # record_name="Generation{}_Scenario{}".format(generation,scenario_counter)
        # record_name = "scenario_" + str(obs_group_num)

        # e2e_time_start = time.time()

        # run_scenario(record_name, obs_folder, obs_group_num)

        # runScenario(record_name, obs_group_number=obs_group_num)
        # e2e_time = time.time() - e2e_time_start
        # obs_group_num += 1

    return obs_group_path_list


# this function costs calculating resources
ptl_dict, ltp_dict, diGraph = initialize()


def adc_routing_generate():
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
    config_file_tuned_status = config_file_generating(generated_individual, option_obj_list, default=True)
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
