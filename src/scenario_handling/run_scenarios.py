import time
import subprocess
from config import MAX_RECORD_TIME, TRAFFIC_LIGHT_MODE
from environment.container_settings import get_container_name
from environment.cyber_env_operation import cyber_env_init
from modules.routing.proto.routing_pb2 import RoutingRequest
from objectives.measure_objectives import measure_objectives_individually
from optimization_algorithms.genetic_algorithm.ga import generate_individuals
from scenario_handling.create_scenarios import create_scenarios
from tools.bridge.CyberBridge import Topics


def register_obstacles(obs_group_path):
    cmd = f"docker exec -d {get_container_name()} /apollo/modules/tools/perception/obstacles_perception.bash " + obs_group_path
    p = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return p


def stop_obstacles(p):
    cmd = f"docker exec -d {get_container_name()} /apollo/scripts/my_scripts/stop_obstacles.sh"
    subprocess.run(cmd.split())


def send_routing_request(init_x, init_y, dest_x, dest_y, bridge):
    routing_request = RoutingRequest()

    # define header
    # routing_request.header.timestamp_sec = cyber_time.Time.now().to_sec()
    routing_request.header.timestamp_sec = time.time()

    routing_request.header.module_name = "routing routing..."
    routing_request.header.sequence_num = 0

    # define way points (start and end)
    start_waypoint = routing_request.waypoint.add()
    start_waypoint.pose.x = init_x
    start_waypoint.pose.y = init_y

    end_waypoint = routing_request.waypoint.add()
    end_waypoint.pose.x = dest_x
    end_waypoint.pose.y = dest_y

    bridge.publish(Topics.RoutingRequest, routing_request.SerializeToString())


def register_obstacles_by_channel(message_handler, obs_perception_messages):
    message_handler.update_obs_msg(obs_perception_messages)
    message_handler.obs_start()


def register_traffic_lights_by_channel(message_handler, traffic_control):
    message_handler.update_traffic_msg(traffic_control)
    message_handler.traffic_lights_start()


def send_routing_request_by_channel(bridge, routing_request_message):
    bridge.publish(Topics.RoutingRequest, routing_request_message.SerializeToString())


def run_scenarios(generated_individual, scenario_list, message_handler):
    # Restart cyber_env
    cyber_env_init()

    scenario_count = 0

    for scenario in scenario_list:
        print(f"  Scenario_{scenario_count}")
        print("    Start recorder...")
        recorder_subprocess = scenario.start_recorder()
        register_obstacles_by_channel(message_handler, scenario.obs_perception_messages)

        if TRAFFIC_LIGHT_MODE == "read":
            register_traffic_lights_by_channel(message_handler, scenario.traffic_control_msg)
        elif TRAFFIC_LIGHT_MODE == "random":
            register_traffic_lights_by_channel(message_handler, scenario.traffic_control_manager)

        send_routing_request_by_channel(message_handler.bridge, scenario.routing_request_message)
        time.sleep(MAX_RECORD_TIME)
        # Stop recording messages and producing perception messages
        print("    Stop recorder...")
        scenario.stop_recorder(recorder_subprocess)

        message_handler.obs_stop()
        message_handler.traffic_lights_stop()

        violation_results, code_coverage, execution_time = measure_objectives_individually(scenario)
        generated_individual.update_accumulated_objectives(violation_results, code_coverage, execution_time)
        generated_individual.update_violation_intro_remov(violation_results, scenario, scenario_count)

        scenario_count += 1


def check_default_running(pre_record_info, config_file_obj, file_output_manager, message_broker):
    default_individual = generate_individuals(config_file_obj, population_size=1)[0]
    name_prefix = "default"
    file_output_manager.output_initial_record2default_mapping(pre_record_info, name_prefix)
    scenario_list = create_scenarios(default_individual, config_file_obj, pre_record_info, name_prefix)
    run_scenarios(default_individual, scenario_list, message_broker)
    file_output_manager.save_violation_results(default_individual, scenario_list)
    file_output_manager.save_default_scenarios()