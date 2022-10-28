import time
import subprocess
from config import MAX_RECORD_TIME
from environment.container_settings import get_container_name
from environment.cyber_env_operation import modules_operation, kill_modules
from modules.routing.proto.routing_pb2 import RoutingRequest
from objectives.measure_objectives import measure_objectives_individually
from tools.bridge.CyberBridge import Topics


def replay_scenario(record_path):
    return


def record_route_info():
    return


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


def run_scenarios(generated_individual, scenario_list, bridge):

    scenario_count = 0

    for scenario in scenario_list:
        print(f"  Scenario_{scenario_count}")
        adc_route_raw = scenario.adc_route.split(',')
        init_x, init_y, dest_x, dest_y = float(adc_route_raw[0]), float(adc_route_raw[1]), float(
            adc_route_raw[2]), float(adc_route_raw[3])

        record_route_info()

        print("    Start recorder...")
        recorder_subprocess = scenario.start_recorder()

        p = register_obstacles(scenario.obs_group_path)

        send_routing_request(init_x, init_y, dest_x, dest_y, bridge)

        # Wait for record time
        time.sleep(MAX_RECORD_TIME)

        # Stop recording messages and producing perception messages
        print("    Stop recorder...")
        scenario.stop_recorder(recorder_subprocess)

        # scenario.stop_subprocess(p)
        stop_obstacles(p)

        violation_number, code_coverage, execution_time = measure_objectives_individually(scenario)
        # scenario.calculate_fitness(violation_number, code_coverage, execution_time)

        # fitness = calculate_fitness(violation_number, code_coverage, execution_time)
        generated_individual.update_accumulated_objectives(violation_number, code_coverage, execution_time)

        if violation_number == 0:
            scenario.delete_record()

        scenario_count += 1

    # return accumulated_fitness
