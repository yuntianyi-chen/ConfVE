import os
import shutil
import signal
import glob
import subprocess
import time
from config import APOLLO_ROOT, TRAFFIC_LIGHT_MODE, APOLLO_RECORDS_DIR
from environment.container_settings import get_container_name
from tools.traffic_light_control.TrafficControlManager import TrafficControlManager


class Scenario:
    def __init__(self, record_name):
        self.record_name = record_name
        self.has_emerged_violations = False
        self.record_path = f"{APOLLO_ROOT}/records/{self.record_name}.00000"

    def update_violations(self):
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

    def start_recorder(self):
        # time.sleep(0.5)
        cmd = f"docker exec -d {get_container_name()} /apollo/bazel-bin/cyber/tools/cyber_recorder/cyber_recorder record -o /apollo/records/{self.record_name} -a &"
        recorder_subprocess = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # time.sleep(1)
        return recorder_subprocess

    def stop_recorder(self, recorder_subprocess):
        cmd = f"docker exec -d {get_container_name()} /apollo/scripts/my_scripts/stop_recorder.sh"
        subprocess.run(cmd.split())
        self.delete_recorder_log()
        time.sleep(0.5)

    def delete_record(self):
        os.remove(f"{APOLLO_RECORDS_DIR}/{self.record_name}.00000")

    def save_record(self, backup_record_file_save_path):
        shutil.copy(f"{APOLLO_RECORDS_DIR}/{self.record_name}.00000",
                    f"{backup_record_file_save_path}/{self.record_name}.00000")

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
