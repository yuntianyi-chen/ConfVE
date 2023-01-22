import time
from config import MAX_RECORD_TIME, TRAFFIC_LIGHT_MODE


def run_scenarios_by_division(scenario_list, containers):
    time.sleep(2)

    sub_scenario_list_list = [scenario_list[x:x + len(containers)] for x in
                              range(0, len(scenario_list), len(containers))]
    for sub_scenario_list in sub_scenario_list_list:
        for scenario, container in zip(sub_scenario_list, containers):
            start_running(scenario, container)
        time.sleep(MAX_RECORD_TIME)
        for container in containers:
            stop_running(container)
        time.sleep(2)

def start_running(scenario, container):
    container.start_recorder(scenario.record_name)
    container.message_handler.register_obstacles_by_channel(scenario.obs_perception_messages)
    if TRAFFIC_LIGHT_MODE == "read":
        container.message_handler.register_traffic_lights_by_channel(scenario.traffic_control_msg)
    elif TRAFFIC_LIGHT_MODE == "random":
        container.message_handler.register_traffic_lights_by_channel(scenario.traffic_control_manager)
    container.message_handler.send_routing_request_by_channel(scenario.routing_request_message)


def stop_running(container):
    container.stop_recorder()
    container.message_handler.obs_stop()
    container.message_handler.traffic_lights_stop()