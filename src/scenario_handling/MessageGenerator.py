import random
import csv
from pandas import read_csv
from tools.hdmap import map_tools
from scenario_handling.InitialScenarioInfo import InitialScenarioInfo
from testing_approaches.scenorita.auxiliary.map_info_parser import initialize, validatePath
from config import MAP_NAME, AV_TESTING_APPROACH, OBS_GROUP_COUNT, MANUAL_ADC_ROUTE_PATH

class MessageGenerator:
    def __init__(self):
        return

    def get_record_info_by_approach(self, scenario_record_dir_path):
        if AV_TESTING_APPROACH != "Random":
            pre_record_info = InitialScenarioInfo(is_record_file=True)
            pre_record_info.update_record_path(scenario_record_dir_path)
            pre_record_info.update_violation_by_measuring()
            pre_record_info.extract_record_info()
        else:
            # Randomly generate
            obs_group_path_list = [self.read_obstacles() for i in range(OBS_GROUP_COUNT)]
            # obs_group_path_list = [self.obs_routing_generate() for i in range(OBS_GROUP_COUNT)]
            adc_routing_list = [self.adc_routing_generate() for i in range(OBS_GROUP_COUNT)]
            # adc_routing_list = [self.read_adc_routes() for i in range(OBS_GROUP_COUNT)]
            # adc_routing_list = ["586980.86,4140959.45,587283.52,4140882.30" for i in obs_group_path_list]
            pre_record_info = InitialScenarioInfo(is_record_file=False)
            pre_record_info.update_generated_info(obs_group_path_list, adc_routing_list)
        return pre_record_info

    def read_adc_routes(self):
        adc_routes_list = []
        with open(MANUAL_ADC_ROUTE_PATH, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                adc_routes_list.append(f'{row["x_start"]},{row["y_start"]},{row["x_end"]},{row["y_end"]}')
        return adc_routes_list

    def read_obstacles(self):
        obs_apollo_folder = f"{MAP_NAME}/obs_in_group/"
        adc_route_csv = read_csv(MANUAL_ADC_ROUTE_PATH)
        recordname_list = adc_route_csv['RecordName'].tolist()
        obs_group_path_list = []
        for obs_group_folder_name in recordname_list:
            obs_group_path_list.append(obs_apollo_folder + obs_group_folder_name)
        return obs_group_path_list

    def obs_routing_generate(self):
        return

    def adc_routing_generate(self):
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

