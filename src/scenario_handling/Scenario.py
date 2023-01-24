import os

from config import TRAFFIC_LIGHT_MODE, APOLLO_RECORDS_DIR
from tools.traffic_light_control.TrafficControlManager import TrafficControlManager


class Scenario:
    def __init__(self, record_name, record_id):
        self.record_id = record_id
        self.has_emerged_violations = False
        self.has_emerged_module_violations = False
        self.update_record_name_and_path(record_name)
        self.confirmed_record_name_list = []

    def update_record_name_and_path(self, new_record_name):
        self.record_name = new_record_name
        self.record_path = f"{APOLLO_RECORDS_DIR}/{self.record_name}.00000"

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




