import time
import subprocess
from threading import Thread
from config import MAX_RECORD_TIME, REPLAY_SCENARIO_RECORD_DIR


def replay_scenario(scenario, container):
    container.modules_operation(operation="start")
    container.stop_sim_control_standalone()
    container.start_sim_control_standalone()
    container.message_handler.send_initial_localization(scenario)

    container.start_recorder(scenario.record_name)
    start_replay(scenario, container)

    time.sleep(MAX_RECORD_TIME)

    container.stop_recorder()
    time.sleep(2)
    container.kill_modules()


def replay_scenarios_in_threading(scenario_list, containers):
    sub_scenario_list_list = [scenario_list[x:x + len(containers)] for x in
                              range(0, len(scenario_list), len(containers))]
    for sub_scenario_list in sub_scenario_list_list:
        thread_list = []
        for scenario, container in zip(sub_scenario_list, containers):
            t_replay = Thread(target=replay_scenario, args=(scenario, container,))
            thread_list.append(t_replay)
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
        time.sleep(1)


def replay_scenarios_by_division(scenario_list, containers):
    sub_scenario_list_list = [scenario_list[x:x + len(containers)] for x in
                              range(0, len(scenario_list), len(containers))]
    for sub_scenario_list in sub_scenario_list_list:
        # print("Restart Modules...")
        for scenario, container in zip(sub_scenario_list, containers):
            container.modules_operation(operation="start")
            # container.stop_sim_control_standalone_v7()
            # container.start_sim_control_standalone_v7(scenario.coord.x, scenario.coord.y, scenario.heading)
            container.stop_sim_control_standalone()
            container.start_sim_control_standalone()
            container.message_handler.send_initial_localization(scenario)
        # time.sleep(3)
        # print("start running")

        for scenario, container in zip(sub_scenario_list, containers):
            container.start_recorder(scenario.record_name)
        # time.sleep(1)

        print("start replaying")
        for scenario, container in zip(sub_scenario_list, containers):
            start_replay(scenario, container)

        # for i in range(10):
        #     time.sleep(1)
        #     print(i+1)
        time.sleep(MAX_RECORD_TIME)
        # print("stop running")
        for container in containers:
            container.stop_recorder()
        time.sleep(2)
        for container in containers:
            container.kill_modules()
        # time.sleep(1)
        # for container in containers:
        #     stop_perception(container)
        time.sleep(1)
    # time.sleep(1)


def start_replay(scenario, container):
    # print(f"{REPLAY_SCENARIO_RECORD_DIR}/{scenario.initial_scenario_record_name}")
    # cmd = f"docker exec -d {container.container_name} /apollo/bazel-bin/cyber/tools/cyber_recorder/cyber_recorder play -f {REPLAY_SCENARIO_RECORD_DIR}/{scenario.initial_scenario_record_name} -c /apollo/routing_request /apollo/perception/obstacles /apollo/perception/traffic_light"
    cmd = f"docker exec -d {container.container_name} /apollo/bazel-bin/cyber/tools/cyber_recorder/cyber_recorder play -f {REPLAY_SCENARIO_RECORD_DIR}/{scenario.initial_scenario_record_name} -c /apollo/routing_response /apollo/perception/obstacles /apollo/perception/traffic_light"
    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# def start_running(scenario, container):
#     container.start_recorder(scenario.record_name)
#     time.sleep(1)
#     start_replay(scenario, container)
# container.message_handler.send_routing_request_by_channel(scenario.routing_request_message)
# container.message_handler.register_obstacles_by_channel(scenario.obs_perception_messages)
# if TRAFFIC_LIGHT_MODE == "read":
#     container.message_handler.register_traffic_lights_by_channel(scenario.traffic_control_msg)
# elif TRAFFIC_LIGHT_MODE == "random":
#     container.message_handler.register_traffic_lights_by_channel(scenario.traffic_control_manager)

#
# def stop_running(container):
#     container.stop_recorder()

#
# def stop_perception(container):
#     container.message_handler.obs_stop()
#     container.message_handler.traffic_lights_stop()
