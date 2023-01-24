import pickle
from datetime import date
from config import PROJECT_ROOT, AV_TESTING_APPROACH, MAP_NAME, MODULE_ORACLES

base_path = f"{PROJECT_ROOT}/data/exp_results/{AV_TESTING_APPROACH}/{MAP_NAME}/2023-01-23"


def dump_default_violation_results_by_pickle(default_violation_results_list):
    time_str = str(date.today())

    # base_path = f"{PROJECT_ROOT}/data/exp_results/{AV_TESTING_APPROACH}/{time_str}"

    default_violation_dump_data_path = f"{base_path}/default_violation_pickle_dump"

    with open(default_violation_dump_data_path, 'wb') as f:
        pickle.dump(default_violation_results_list, f, protocol=4)


def load_default_violation_results_by_pickle(default_violation_load_data_path):

    default_violation_results_list = pickle.load(open(default_violation_load_data_path, 'rb'))
    return default_violation_results_list


if __name__ == '__main__':
    default_violation_load_data_path = f"{base_path}/default_violation_pickle"
    default_violation_results_list = load_default_violation_results_by_pickle(default_violation_load_data_path)

    print(default_violation_results_list)

    new_list =[]
    for default_violations in default_violation_results_list:
        sid = default_violations[0]
        temp_list = []
        for item in default_violations[1]:
            if item.main_type not in MODULE_ORACLES:
                temp_list.append(item)
        new_list.append((sid,temp_list))

    dump_default_violation_results_by_pickle(new_list)
