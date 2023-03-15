import random
import csv
from pandas import read_csv
from tools.hdmap import map_tools
from testing_approaches.scenorita.auxiliary.map_info_parser import initialize, validatePath
from config import MAP_NAME, MANUAL_ADC_ROUTE_PATH

def read_adc_routes():
    adc_routes_list = []
    with open(MANUAL_ADC_ROUTE_PATH, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            adc_routes_list.append(f'{row["x_start"]},{row["y_start"]},{row["x_end"]},{row["y_end"]}')
    return adc_routes_list

def read_obstacles():
    obs_apollo_folder = f"{MAP_NAME}/obs_in_group/"
    adc_route_csv = read_csv(MANUAL_ADC_ROUTE_PATH)
    recordname_list = adc_route_csv['RecordName'].tolist()
    obs_group_path_list = []
    for obs_group_folder_name in recordname_list:
        obs_group_path_list.append(obs_apollo_folder + obs_group_folder_name)
    return obs_group_path_list

def obs_routing_generate():
    return

def adc_routing_generate():
    # this function costs calculating resources
    ptl_dict, ltp_dict, diGraph, obs_diGraph = initialize()

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
