import time
from config import MAX_RECORD_TIME, TRAFFIC_LIGHT_MODE


def run_scenarios_by_division(scenario_list, containers):
    sub_scenario_list_list = [scenario_list[x:x + len(containers)] for x in
                              range(0, len(scenario_list), len(containers))]
    for sub_scenario_list in sub_scenario_list_list:
        # print("Restart Modules...")
        for scenario, container in zip(sub_scenario_list, containers):
            container.modules_operation(operation="start")
            container.stop_sim_control_standalone()
            container.start_sim_control_standalone()
            container.message_handler.send_initial_localization(scenario)
        time.sleep(0.5)
        # print("start running")
        for scenario, container in zip(sub_scenario_list, containers):
            start_running(scenario, container)
        time.sleep(MAX_RECORD_TIME-3)
        # print("stop running")
        for container in containers:
            stop_running(container)
        time.sleep(3)
        for container in containers:
            container.kill_modules()
        for container in containers:
            stop_perception(container)
        time.sleep(1)
    time.sleep(1)


def start_running(scenario, container):
    container.message_handler.send_routing_request_by_channel(scenario.routing_request_message)
    container.message_handler.register_obstacles_by_channel(scenario.obs_perception_messages)
    if TRAFFIC_LIGHT_MODE == "read":
        container.message_handler.register_traffic_lights_by_channel(scenario.traffic_control_msg)
    elif TRAFFIC_LIGHT_MODE == "random":
        container.message_handler.register_traffic_lights_by_channel(scenario.traffic_control_manager)
    container.start_recorder(scenario.record_name)


def stop_running(container):
    container.stop_recorder()


def stop_perception(container):
    container.message_handler.obs_stop()
    container.message_handler.traffic_lights_stop()
