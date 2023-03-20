import os
from pathlib import Path
from typing import List, Tuple, Dict, Set

from cyber_record.record import Record
from shapely.geometry import LineString

from config import TRAFFIC_LIGHT_MODE, APOLLO_RECORDS_DIR
from objectives.violation_number.oracles import RecordAnalyzer
from tools.traffic_light_control.TrafficControlManager import TrafficControlManager
from tools.utils import extract_main_decision


class Scenario:
    def __init__(self, record_name, record_id):
        self.record_id = record_id
        self.has_emerged_violations = False
        self.has_emerged_module_violations = False
        self.update_record_name_and_path(record_name)
        # self.confirmed_record_name_list = []

    def update_record_name_and_path(self, new_record_name):
        self.record_name = new_record_name
        self.record_path = f"{APOLLO_RECORDS_DIR}/{self.record_name}.00000"

    def measure_violations(self):
        ra = RecordAnalyzer(self.record_path)
        results = ra.analyze()
        if len(results) > 0:
            print(f"  Record Path: {self.record_path}")
            print(f"    Violation Results: {[(violation.main_type, violation.key_label) for violation in results]}")
        return results

    def analyze_decision_and_sinuosity(self):
        # MapLoader(map_name).load_map_data()
        # ra = RecordAnalyzer(record_file)
        # ra.analyze()
        # feature_violation = ra.oracle_manager.get_counts_wrt_oracle()
        record = Record(self.record_path)
        decisions: Set[Tuple] = set()
        for _, msg, _ in record.read_messages("/apollo/planning"):
            decisions = decisions | extract_main_decision(msg)

        decision_count = len(decisions)
        # feature_decision = {"decisions": len(decisions)}

        coordinates: List[Tuple[float, float]] = list()
        for _, msg, t in record.read_messages("/apollo/localization/pose"):
            new_coordinate = (msg.pose.position.x, msg.pose.position.y)
            if len(coordinates) > 0 and coordinates[-1] == new_coordinate:
                continue
            else:
                coordinates.append(new_coordinate)
        if len(coordinates) < 2:
            sinuosity = 0
        else:
            ego_trajectory = LineString(coordinates)
            start_point = ego_trajectory.interpolate(0, normalized=True)
            end_point = ego_trajectory.interpolate(1, normalized=True)
            shortest_path = LineString([start_point, end_point])
            if shortest_path.length == 0:
                sinuosity = 0
            else:
                sinuosity = ego_trajectory.length / shortest_path.length
        # feature_sinuosity = {"sinuosity": sinuosity}

        # result = feature_violation | feature_decision | feature_sinuosity
        # result = dict(**feature_violation, **feature_decision, **feature_sinuosity)
        # result["filename"] = str(record_file)
        # return result
        return decision_count, sinuosity

    def update_emerged_status(self, violations_emerged_results, contain_module_violation):
        if len(violations_emerged_results) > 0:
            self.has_emerged_violations = True
            if contain_module_violation:
                self.has_emerged_module_violations = True

    def delete_record(self):
        delete_path = f"{APOLLO_RECORDS_DIR}/{self.record_name}.00000"
        if os.path.exists(delete_path):
            os.remove(delete_path)

    def update_traffic_lights(self, traffic_light_control):
        if TRAFFIC_LIGHT_MODE == "read":
            self.traffic_control_msg = traffic_light_control
        elif TRAFFIC_LIGHT_MODE == "random":
            traffic_control_manager = TrafficControlManager(traffic_light_control)
            self.traffic_control_manager = traffic_control_manager

    def update_obs_adc(self, obs_group_path, adc_route):
        self.obs_group_path = obs_group_path
        self.adc_route = adc_route

    def update_config_file_status(self, config_file_status):
        self.config_file_status = config_file_status

    def update_routing_perception_info(self, pre_record_info):
        self.obs_perception_messages = pre_record_info.obs_perception_list
        self.routing_request_message = pre_record_info.routing_request

    def update_original_violations(self, pre_record_info):
        self.original_violation_num = pre_record_info.violation_num
        self.original_violation_results = pre_record_info.violation_results

    def update_coord_heading(self, pre_record_info):
        self.coord = pre_record_info.coord
        self.heading = pre_record_info.heading

    def update_record_info(self, pre_record_info):
        self.update_original_violations(pre_record_info)
        self.update_routing_perception_info(pre_record_info)
        self.update_coord_heading(pre_record_info)
        self.initial_scenario_record_path = pre_record_info.record_file_path
        self.initial_scenario_record_name = pre_record_info.record_name
