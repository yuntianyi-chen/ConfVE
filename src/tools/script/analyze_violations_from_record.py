from os import listdir
from config import INITIAL_SCENARIO_RECORD_DIR, BACKUP_RECORD_SAVE_DIR
from environment.MapLoader import MapLoader
from objectives.measure_objectives import measure_violation_number

if __name__ == '__main__':
    SINGLE_TEST = True
    MapLoader()
    # record_dir = INITIAL_SCENARIO_RECORD_DIR
    record_dir = f"{BACKUP_RECORD_SAVE_DIR}/2023-01-16"

    file_list = listdir(record_dir)
    file_list.sort()
    results = []
    if SINGLE_TEST == True:
        single_file_name = "Generation_0_Config_0_Scenario_4_rerun_0.00000"
        # single_file_name = "Generation_8_Config_41_Obs_0.00000"
        if single_file_name in file_list:
            result = measure_violation_number(f"{record_dir}/{single_file_name}")
            results.append(result)
    else:
        for i in file_list:
            result = measure_violation_number(f"{record_dir}/{i}")
            results.append(result)

    stat_dict = {}
    for i in results:
        for j in i:
            if j not in stat_dict:
                stat_dict[j] = 1
            else:
                stat_dict[j] += 1
    print(stat_dict)