import random
import csv
from os import listdir
from pandas import read_csv
from tools.hdmap import map_tools
from scenario_handling.InitialRecordInfo import InitialRecordInfo
from testing_approaches.scenorita.auxiliary.map_info_parser import initialize, validatePath
from config import MAP_NAME, AV_TESTING_APPROACH, MANUAL_ADC_ROUTE_PATH, MAX_INITIAL_SCENARIOS


class MessageGenerator:
    def __init__(self, scenario_record_dir_path):
        self.scenario_record_dir_path = scenario_record_dir_path
        self.scenario_record_path_list = []
        self.total_records_count = 0
        self.get_record_path_list()

        self.pre_record_info_list = []

        self.violation_results_list = []
        self.violation_num_list = []

        self.record_counter = 0

    def update_total_violation_results(self):
        self.violation_results_list = [pri.violation_results for pri in self.pre_record_info_list]
        self.violation_num_list = [len(vr) for vr in self.violation_results_list]
        print("Records Info:")
        print(self.violation_num_list)

    def update_all_records_violatioin_directly(self, violation_results_list):
        for pre_record_info, violation_results in zip(self.pre_record_info_list, violation_results_list):
            pre_record_info.update_violation_directly(violation_results)
        self.update_total_violation_results()

    def get_record_path_list(self):
        scenario_recordname_list = listdir(self.scenario_record_dir_path)
        scenario_recordname_list.sort()
        self.scenario_record_path_list = [f"{self.scenario_record_dir_path}/{recordname}" for recordname in
                                          scenario_recordname_list]
        self.total_records_count = len(self.scenario_record_path_list)

    def update_selected_records_violatioin_directly(self, violation_results_list_with_sid):
        for sid, violation_results in violation_results_list_with_sid:
            for i in range(len(self.pre_record_info_list)):
                if sid == self.pre_record_info_list[i].record_id:
                    self.pre_record_info_list[i].update_violation_directly(violation_results)
        self.update_total_violation_results()

    def replace_records(self, replaced_id_list):
        for rid in replaced_id_list:
            if len(self.scenario_record_path_list) > self.record_counter:
                print(f"Replacing Record_{rid}...")
                for i in range(len(self.pre_record_info_list)):
                    if rid == self.pre_record_info_list[i].record_id:
                        pre_record_info = InitialRecordInfo(True, self.record_counter,
                                                            self.scenario_record_path_list[self.record_counter])
                        self.record_counter += 1
                        self.pre_record_info_list[i] = pre_record_info
        self.update_total_violation_results()

    def replace_record(self, rid):
        if len(self.scenario_record_path_list) > self.record_counter:
            print(f"Replacing Record_{rid}...")
            for i in range(len(self.pre_record_info_list)):
                if rid == self.pre_record_info_list[i].record_id:
                    pre_record_info = InitialRecordInfo(True, self.record_counter,
                                                        self.scenario_record_path_list[self.record_counter])
                    self.record_counter += 1
                    self.pre_record_info_list[i] = pre_record_info
                    return pre_record_info
        # return pre_record_info

    def update_rerun_status(self):
        for p in self.pre_record_info_list:
            p.finished_rerun = True

    def get_not_rerun_record(self):
        return [p for p in self.pre_record_info_list if not p.finished_rerun]

    def get_record_info_by_approach(self):
        if AV_TESTING_APPROACH != "Random":
            for i in range(MAX_INITIAL_SCENARIOS):
                pre_record_info = InitialRecordInfo(True, self.record_counter,
                                                    self.scenario_record_path_list[self.record_counter])
                self.record_counter += 1
                self.pre_record_info_list.append(pre_record_info)
            self.update_total_violation_results()
        # else:
        #     # Randomly generate
        #     obs_group_path_list = [self.read_obstacles() for i in range(OBS_GROUP_COUNT)]
        #     # obs_group_path_list = [self.obs_routing_generate() for i in range(OBS_GROUP_COUNT)]
        #     adc_routing_list = [self.adc_routing_generate() for i in range(OBS_GROUP_COUNT)]
        #     # adc_routing_list = [self.read_adc_routes() for i in range(OBS_GROUP_COUNT)]
        #     # adc_routing_list = ["586980.86,4140959.45,587283.52,4140882.30" for i in obs_group_path_list]
        #     pre_record_info = InitialRecordInfo(is_record_file=False)
        #     pre_record_info.update_generated_info(obs_group_path_list, adc_routing_list)
        #     pre_record_info_list.append(pre_record_info)

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
