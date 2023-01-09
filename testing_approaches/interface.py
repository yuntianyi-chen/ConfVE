import os
import random
import csv
from os import listdir

from cyber_record.record import Record
from pandas import read_csv
from config import MAP_NAME, AV_TESTING_APPROACH, OBS_GROUP_COUNT, ADC_ROUTE_PATH, \
    DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR, INITIAL_SCENARIO_RECORD_DIR
from environment.container_settings import init_settings
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacle

from modules.common.proto.geometry_pb2 import Point3D
from objectives.violation_number.oracles import RecordAnalyzer
from scenario_handling.scenario_tools.map_info_parser import initialize, validatePath
from scenario_handling.scenario_tools import map_tools

# RecordInfo or Generated Info
class InitialScenarioInfo:
    def __init__(self, is_record_file):
        self.is_record_file = is_record_file

    def update_generated_info(self, obs_group_path_list, adc_routing_list):
        self.obs_group_path_list = obs_group_path_list
        self.adc_routing_list = adc_routing_list
        self.count = len(obs_group_path_list)

    def update_record_info(self, scenario_record_file_list, obs_perception_list, routing_request_list):
        self.scenario_record_file_list = scenario_record_file_list
        self.obs_perception_list = obs_perception_list
        self.routing_request_list = routing_request_list
        self.count = len(scenario_record_file_list)

    def update_violation(self, violation_results_list, violation_num_list):
        self.violation_results_list = violation_results_list
        self.violation_num_list = violation_num_list


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


def obs_instance(perception_obstacle):
    points=[]
    for pp in list(perception_obstacle.polygon_point):
        p = Point3D(x=pp.x, y=pp.y, z=pp.z)
        points.append(p)

    obs = PerceptionObstacle(
        id= perception_obstacle.id,
        position=Point3D(x=perception_obstacle.position.x, y=perception_obstacle.position.y, z=perception_obstacle.position.z),
        theta=perception_obstacle.theta,
        velocity=Point3D(x=perception_obstacle.velocity.x, y=perception_obstacle.velocity.y, z=perception_obstacle.velocity.z),
        acceleration=Point3D(x=perception_obstacle.acceleration.x, y=perception_obstacle.acceleration.y, z=perception_obstacle.acceleration.z),
        length=perception_obstacle.length,
        width=perception_obstacle.width,
        height=perception_obstacle.height,
        type=perception_obstacle.type,
        timestamp=perception_obstacle.timestamp,
        tracking_time=perception_obstacle.tracking_time,
        polygon_point=points
    )

    # obs = PerceptionObstacle(perception_obstacle)
    return obs

def extract_routing_perception_info(scenario_record_dir_path):
    scenario_recordname_list = os.listdir(scenario_record_dir_path)
    scenario_recordname_list.sort()
    scenario_record_file_list = [f"{scenario_record_dir_path}/{recordname}" for recordname in scenario_recordname_list]

    obs_perception_list = []
    routing_request_list=[]
    for scenario_record_file_path in scenario_record_file_list:
        record = Record(scenario_record_file_path)
        temp_list=[]
        for topic, message, t in record.read_messages():
            if topic == "/apollo/perception/obstacles":
                perception_obstacles = list(message.perception_obstacle)
                obs_instance_list = [obs_instance(perception_obstacle) for perception_obstacle in perception_obstacles]
                # temp_list.append((message.header.sequence_num, perception_obstacle))
                temp_list.append(obs_instance_list)
            elif topic == "/apollo/routing_response":
                if message.routing_request.header.module_name == "routing routing...":
                    routing_request = message.routing_request
                    routing_request_list.append(routing_request)
        obs_perception_list.append(temp_list)
    return obs_perception_list, routing_request_list

# obs_perception, adc_routing, violation_results, violation_num
def get_record_info_by_approach(obs_perception_list, routing_request_list, scenario_record_dir_path):
    if AV_TESTING_APPROACH == "scenoRITA":
        # adc_route_csv = read_csv(ADC_ROUTE_PATH)
        # recordname_list = adc_route_csv['RecordName'].tolist()

        scenario_recordname_list = listdir(scenario_record_dir_path)
        scenario_recordname_list.sort()
        scenario_record_file_list = [f"{scenario_record_dir_path}/{recordname}" for recordname in scenario_recordname_list]

        # obs_perception_list, routing_request_list = extract_routing_perception_info(scenario_record_file_list)

        pre_record_info = InitialScenarioInfo(is_record_file=True)

        pre_record_info.update_record_info(scenario_record_file_list, obs_perception_list, routing_request_list)

        violation_results_list, violation_num_list = read_violation_num(scenario_record_file_list)
        pre_record_info.update_violation(violation_results_list, violation_num_list)

    else:
        # Randomly generate
        obs_group_path_list = [obs_routing_generate() for i in range(OBS_GROUP_COUNT)]
        adc_routing_list = [adc_routing_generate() for i in range(OBS_GROUP_COUNT)]
        # adc_routing_list = ["586980.86,4140959.45,587283.52,4140882.30" for i in obs_group_path_list]
        pre_record_info = InitialScenarioInfo(is_record_file=False)
        pre_record_info.update_generated_info(obs_group_path_list, adc_routing_list)

    return pre_record_info


def read_violation_num(file_list):
    violation_num_list = []

    violation_results_list = []
    for i in file_list:
        ra = RecordAnalyzer(i)
        results = ra.analyze()
        # print(f"      Violation Results: {results}")
        violation_results_list.append(results)
        violation_num_list.append(len(results))

        print((f"id:{i}", f"Vio Count:{len(results)}", results))
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

    file_list = [f"{DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR}/{i}.00000" for i in recordname_list]
    results_list = []
    for i in file_list:
        ra = RecordAnalyzer(i)
        results = ra.analyze()
        # print(f"      Violation Results: {results}")
        results_list.append(results)
        violation_num_list.append(len(results))

    print(results_list)
    print(violation_num_list)
