from datetime import date
from os import listdir
from config import INITIAL_SCENARIO_RECORD_DIR, BACKUP_RECORD_SAVE_DIR, DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR, \
    PROJECT_ROOT, AV_TESTING_APPROACH
from environment.MapLoader import MapLoader
from objectives.measure_objectives import measure_violation_number
from tools.script.pickle_file_handling import dump_default_violation_results_by_pickle

if __name__ == '__main__':
    TEST_MODE = "multi"
    MapLoader()
    record_dir = INITIAL_SCENARIO_RECORD_DIR
    # record_dir = DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR

    # record_dir = f"{BACKUP_RECORD_SAVE_DIR}/2023-01-16"

    file_list = listdir(record_dir)
    file_list.sort()
    results = []
    violations_results_list_list=[]
    if TEST_MODE == "single":
        single_file_name = "Generation_0_Config_0_Scenario_4_rerun_0.00000"
        # single_file_name = "Generation_8_Config_41_Obs_0.00000"
        if single_file_name in file_list:
            result = measure_violation_number(f"{record_dir}/{single_file_name}")
            results.append(result)
    elif TEST_MODE == "multi":
        for i in file_list:
            result = measure_violation_number(f"{record_dir}/{i}")
            results.append(result)
    else:

        time_str = str(date.today())

        base_path = f"{PROJECT_ROOT}/data/exp_results/{AV_TESTING_APPROACH}/{time_str}"

        default_violation_dump_data_path = f"{base_path}/default_violation_pickle_dump"

        sub_file_list_list = [file_list[x:x + 10] for x in range(0, len(file_list), 10)]
        for sub_list in sub_file_list_list:
            all_emerged_results = []
            for i in sub_list:
                result = measure_violation_number(f"{record_dir}/{i}")
                results.append(result)
                for violation in result:
                    if violation not in all_emerged_results:
                        all_emerged_results.append(violation)
            violations_results_list_list.append(all_emerged_results)

        dump_default_violation_results_by_pickle(violations_results_list_list)

    stat_dict = {}
    for i in results:
        for j in i:
            if j not in stat_dict:
                stat_dict[j] = 1
            else:
                stat_dict[j] += 1
    print(stat_dict)


