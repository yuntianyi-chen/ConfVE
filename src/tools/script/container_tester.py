import subprocess
import time

from config import APOLLO_ROOT, REPLAY_SCENARIO_RECORD_DIR, INITIAL_SCENARIO_RECORD_DIR, MAX_RECORD_TIME, \
    DEFAULT_CONFIG_FILE_PATH
from config_file_handler.ApolloParser import ApolloParser
from environment.Container import Container
from environment.MapLoader import MapLoader
from objectives.violation_number.oracles import RecordAnalyzer
from scenario_handling.InitialRecordInfo import InitialRecordInfo
from scenario_handling.Scenario import Scenario


def start_replay(ctn, scenario):
    cmd = f"docker exec -d {ctn.container_name} /apollo/bazel-bin/cyber/tools/cyber_recorder/cyber_recorder play -f /apollo/initial/test/{scenario.record_name}.00000 -c /apollo/routing_response /apollo/perception/obstacles /apollo/perception/traffic_light"
    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# "cyber_recorder play -f /apollo/records/Generation_0_Config_0_Scenario_2.00000 -c /apollo/routing_request /apollo/perception/obstacles /apollo/perception/traffic_light"

if __name__ == '__main__':
    config_file_obj = ApolloParser.config_file_parser2obj(DEFAULT_CONFIG_FILE_PATH)

    # ctn = Container(APOLLO_ROOT, f'ROUTE_0')
    ctn = Container(APOLLO_ROOT, f'cloudsky')

    map_instance = MapLoader().map_instance

    ctn.start_instance()
    ctn.cyber_env_init()
    ctn.connect_bridge()
    ctn.create_message_handler(map_instance)

    print(f'Dreamview at http://{ctn.ip}:{ctn.port}')

    # scenario = Scenario(record_name="Init_Config_12_Scenario_5", record_id="none")
    scenario = Scenario(record_name="00000046", record_id="none")

    # pre_record_info = InitialRecordInfo(True, 0, scenario.record_name, scenario.record_path)
    # dir_path = "/home/cloudsky/Research/Apollo/Backup/useful_cases"

    source_record_path=f"{APOLLO_ROOT}/initial/test/{scenario.record_name}.00000"
    pre_record_info = InitialRecordInfo(True, 0, scenario.record_name, source_record_path)
    # pre_record_info.update_violation_by_measuring()

    ra = RecordAnalyzer(source_record_path)
    print(ra.analyze())

    scenario.update_record_info(pre_record_info)
    traffic_light_control = pre_record_info.traffic_lights_list
    scenario.update_traffic_lights(traffic_light_control)

    ctn.modules_operation(operation="start")
    # ctn.stop_sim_control_standalone_v7()
    # ctn.start_sim_control_standalone_v7(scenario.coord.x, scenario.coord.y, scenario.heading)
    ctn.stop_sim_control_standalone()
    ctn.start_sim_control_standalone()
    ctn.message_handler.send_initial_localization(scenario)

    ctn.start_recorder(scenario.record_name)
    start_replay(ctn, scenario)

    time.sleep(MAX_RECORD_TIME)

    ctn.stop_recorder()
    time.sleep(2)
    ctn.kill_modules()

    ra = RecordAnalyzer(scenario.record_path)
    print(ra.analyze())
