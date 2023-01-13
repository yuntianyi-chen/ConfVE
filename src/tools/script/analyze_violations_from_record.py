from os import listdir

from environment.MapLoader import MapLoader
# from environment.container_settings import load_map_data
from objectives.measure_objectives import measure_violation_number

if __name__ == '__main__':
    SINGLE_TEST = False
    MapLoader()
    record_dir = "/home/cloudsky/Research/Apollo/Backup/scenoRITA/records/using"
    file_list = listdir(record_dir)
    file_list.sort()
    results = []
    if SINGLE_TEST == True:
        single_file_name = "Generation36_Scenario33.00000"
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