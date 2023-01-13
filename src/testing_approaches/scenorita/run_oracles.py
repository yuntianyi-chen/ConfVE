import os
from multiprocessing import Process, Manager
from config import APOLLO_RECORDS_DIR
from testing_approaches.scenorita.grading_metrics import acceleration, speeding, collision

# TEMP_OUTPUT_PATH = '/apollo/automation/temp_record/'
# TEMP_OUTPUT_PATH = APOLLO_ROOT + "/records/"
TEMP_OUTPUT_PATH = f"{APOLLO_RECORDS_DIR}/"
# OUTPUT_NAME = 'output'

def run_oracles(record_name):
    target_output_names = []

    all_output_names = os.listdir(TEMP_OUTPUT_PATH)
    all_output_names.sort()

    for name in all_output_names:
        if name.startswith(f'{record_name}.'):
            target_output_names.append(name)

    processes = []
    manager = Manager()
    oracle_results = manager.dict()

    for output_name in target_output_names:        # run checks on each output
        output_path = f'{TEMP_OUTPUT_PATH}{output_name}'

        processes.append(
            Process(target=acceleration.walk_messages,
                    args=(output_path, 4),
                    kwargs={'return_dict': oracle_results}))
        processes.append(
            Process(target=acceleration.walk_messages,
                    args=(output_path, -4),
                    kwargs={'return_dict': oracle_results}))
        processes.append(
            Process(target=collision.walk_messages,
                    args=(output_path,),
                    kwargs={'return_dict': oracle_results}))
        processes.append(
            Process(target=speeding.walk_messages,
                    args=(output_path,),
                    kwargs={'return_dict': oracle_results}))

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    accl = oracle_results['accl']
    hardbreak = oracle_results['hardbreak']
    min_dist = oracle_results['min_dist']
    collision_states = oracle_results['collision_states']
    min_speed = oracle_results['min_speed']
    traveled_lanes = oracle_results['traveled_lanes']
    boundary_dist = oracle_results['boundary_dist']

    return min_dist, traveled_lanes, min_speed, boundary_dist, accl, hardbreak, collision_states
