from config import TRAFFIC_LIGHT_MODE, APOLLO_RECORDS_DIR
from tools.traffic_light_control.TrafficControlManager import TrafficControlManager


class Scenario:
    def __init__(self, record_name, scenario_id):
        self.scenario_id = scenario_id
        self.has_emerged_violations = False
        self.update_record_name_and_path(record_name)
        self.confirmed_record_name_list = []

    def update_record_name_and_path(self, new_record_name):
        self.record_name = new_record_name
        self.record_path = f"{APOLLO_RECORDS_DIR}/{self.record_name}.00000"

    def update_emerged_status(self, violations_emerged_results):
        if len(violations_emerged_results) > 0:
            self.has_emerged_violations = True

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

    def update_routing_perception_info(self, obs_perception_messages, routing_request_message):
        self.obs_perception_messages = obs_perception_messages
        self.routing_request_message = routing_request_message

    def update_original_violations(self, violation_num, violation_results):
        self.original_violation_num = violation_num
        self.original_violation_results = violation_results



