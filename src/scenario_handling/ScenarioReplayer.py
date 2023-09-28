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
    container.connect_bridge()
    container.message_handler.update_bridge(container.bridge)


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


def start_replay(scenario, container):
    cmd = f"docker exec -d {container.container_name} /apollo/bazel-bin/cyber/tools/cyber_recorder/cyber_recorder play -f {REPLAY_SCENARIO_RECORD_DIR}/{scenario.initial_scenario_record_name} -c /apollo/routing_response /apollo/perception/obstacles /apollo/perception/traffic_light"
    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
