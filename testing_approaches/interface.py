import os
import random
import csv
from pandas import read_csv
from config import APOLLO_ROOT, MAP_NAME, AV_TESTING_APPROACH, OBS_DIR, OBS_GROUP_COUNT, ADC_ROUTE_PATH, \
    USING_PRE_RECORD_DIR
from environment.container_settings import init_settings
from objectives.violation_number.oracles import RecordAnalyzer
from scenario_handling.scenario_tools.map_info_parser import initialize, validatePath
# from testing_approaches.obstacle_obj import ObsWithFitness
# from testing_approaches.scenorita.interface import ScenoRITA
from scenario_handling.scenario_tools import map_tools


# def init_obs():
#     obstacle_chromosomes_list = [ObsWithFitness() for i in range(OBS_GROUP_COUNT)]
#     return obstacle_chromosomes_list
#
class RecordInfo:
    def __init__(self, obs_group_path_list, adc_routing_list):
        self.obs_group_path_list = obs_group_path_list
        self.adc_routing_list = adc_routing_list

    def update_violation(self, violation_results_list, violation_num_list):
        self.violation_results_list =violation_results_list
        self.violation_num_list= violation_num_list

def obs_routing_generate():
    return

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

def get_record_info_by_approach():
    # approach_generator = None
    # obs_group_path_list = []
    # adc_routing_list = []

    if AV_TESTING_APPROACH == "scenoRITA":
        # approach_generator = ScenoRITA()
        obs_group_path_list = read_obstacles()
        adc_routing_list = read_adc_routes()
        pre_record_info = RecordInfo(obs_group_path_list, adc_routing_list)
        violation_results_list, violation_num_list = read_violation_num()
        pre_record_info.update_violation(violation_results_list, violation_num_list)

    else:
        # Randomly generate
        obs_group_path_list = [obs_routing_generate() for i in range(OBS_GROUP_COUNT)]
        adc_routing_list = [adc_routing_generate() for i in range(OBS_GROUP_COUNT)]
        violation_num_list = [None for i in range(OBS_GROUP_COUNT)]
        pre_record_info = RecordInfo(obs_group_path_list, adc_routing_list)

    # adc_routing = adc_routing_generate()
    # adc_routing_list = ["586980.86,4140959.45,587283.52,4140882.30" for i in obs_group_path_list]

    return pre_record_info

def read_violation_num():
    adc_route_csv = read_csv(ADC_ROUTE_PATH)
    recordname_list = adc_route_csv['RecordName'].tolist()

    violation_num_list = []

    file_list = [f"{USING_PRE_RECORD_DIR}/{i}.00000" for i in recordname_list]
    violation_results_list=[]
    for i in file_list:
        ra = RecordAnalyzer(i)
        results = ra.analyze()
        # print(f"      Violation Results: {results}")
        violation_results_list.append(results)
        violation_num_list.append(len(results))

    print(violation_results_list)
    print(violation_num_list)
    return violation_results_list, violation_num_list

def read_adc_routes():
    adc_routes_list = []
    with open(ADC_ROUTE_PATH, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            adc_routes_list.append(f'{row["x_start"]},{row["y_start"]},{row["x_end"]},{row["y_end"]}')
    return adc_routes_list

def read_obstacles():
    # obs_folder = f"{OBS_DIR}/obs_in_group/"
    obs_apollo_folder = f"{MAP_NAME}/obs_in_group/"

    adc_route_csv = read_csv(ADC_ROUTE_PATH)
    recordname_list = adc_route_csv['RecordName'].tolist()

    # obs_group_folders_name_list = os.listdir(obs_folder)
    # obs_group_folders_name_list.sort()
    obs_group_path_list = []
    for obs_group_folder_name in recordname_list:
        obs_group_path_list.append(obs_apollo_folder + obs_group_folder_name)
    return obs_group_path_list


if __name__ == '__main__':
    # obs_group_path_list = read_obstacles()
    # print(obs_group_path_list)

    # adc_routing_list = read_adc_routes()
    # adc_routing_list = [adc_routing_generate() for i in range(OBS_GROUP_COUNT)]
    # print(adc_routing_list)

    init_settings()

    adc_route_csv = read_csv(ADC_ROUTE_PATH)
    recordname_list = adc_route_csv['RecordName'].tolist()

    violation_num_list = []

    file_list = [f"{USING_PRE_RECORD_DIR}/{i}.00000" for i in recordname_list]
    results_list=[]
    for i in file_list:
        ra = RecordAnalyzer(i)
        results = ra.analyze()
        # print(f"      Violation Results: {results}")
        results_list.append(results)
        violation_num_list.append(len(results))

    print(results_list)
    print(violation_num_list)

