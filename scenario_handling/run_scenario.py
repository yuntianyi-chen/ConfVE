# The main script for replaying augmented test bags
# and storing the planning outputs

# import debugpy
# debugpy.listen(5724)
# debugpy.wait_for_client()

# import ptvsd
# ptvsd.enable_attach(address=('localhost', 5724), redirect_output=True)
# # print('Now is a good time to attach your debugger: Run: Python: Attach')
# ptvsd.wait_for_attach()

import os
import time
import signal
import subprocess

from apollo.CyberBridge import Topics
from config import MAX_RECORD_TIME
from environment.container_settings import get_container_name
from environment.cyber_env_operation import modules_operation
from modules.routing.proto.routing_pb2 import RoutingRequest


# from run_scenarios.auxiliary.routing import send_routing_request
# from run_scenarios.grading_metrics import acceleration, speeding, collision

# try:
#     from subprocess import DEVNULL  # Python 3.
# except ImportError:
#     DEVNULL = open(os.devnull, 'wb')
#

# RECORDER_PATH = '/apollo/scripts/record_bag.py'
# USE_CSV_ROUTING = False
# OUTPUT_NAME = 'output'

# Stores output record files from simulation
# TEMP_OUTPUT_PATH = '/apollo/apollo_v7_testing/temp_record/'


def replay_scenario(record_path):
    return


def record_route_info():
    return


def register_obstacles(obs_group_path):
    # Start recording messages and producing perception messages
    # obstacles_perception_cmd='/apollo/modules/tools/perception/obstacles_perception.bash '+MAP_NAME+'/obs_group_'+obs_group_number
    # print(obstacles_perception_cmd)
    # cmd = ['/apollo/modules/tools/perception/obstacles_perception.bash', MAP_NAME + '/obs_group_' + obs_group_number]
    cmd = f"docker exec -d {get_container_name()} /apollo/modules/tools/perception/obstacles_perception.bash " + obs_group_path
    p = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return p


def stop_obstacles(p):
    try:
        os.kill(p.pid, signal.SIGINT)
        p.kill()
    except OSError:
        print("stopped")


def send_routing_request(init_x, init_y, dest_x, dest_y, bridge):
    routing_request = RoutingRequest()

    # define header
    # routing_request.header.timestamp_sec = cyber_time.Time.now().to_sec()
    routing_request.header.timestamp_sec = time.time()

    routing_request.header.module_name = "automation routing"
    routing_request.header.sequence_num = 0

    # define way points (start and end)
    start_waypoint = routing_request.waypoint.add()
    start_waypoint.pose.x = init_x
    start_waypoint.pose.y = init_y

    end_waypoint = routing_request.waypoint.add()
    end_waypoint.pose.x = dest_x
    end_waypoint.pose.y = dest_y

    bridge.publish(Topics.RoutingRequest, routing_request.SerializeToString())


def run_scenarios(scenario_list, bridge):
    print("Restart modules...")
    modules_operation(operation="stop")
    time.sleep(2)
    modules_operation(operation="start")
    time.sleep(2)

    scenario_count = 0
    for scenario in scenario_list:
        print(f"Scenario{scenario_count}")
        adc_route_raw = scenario.adc_route.split(',')
        init_x, init_y, dest_x, dest_y = float(adc_route_raw[0]), float(adc_route_raw[1]), float(
            adc_route_raw[2]), float(adc_route_raw[3])

        record_route_info()

        print("  Start recorder...")
        scenario.start_recorder()

        p = register_obstacles(scenario.obs_group_path)

        send_routing_request(init_x, init_y, dest_x, dest_y, bridge)

        # Wait for record time
        time.sleep(MAX_RECORD_TIME)

        # Stop recording messages and producing perception messages
        print("  Stop recorder...")
        scenario.stop_recorder()

        stop_obstacles(p)
        scenario_count += 1
