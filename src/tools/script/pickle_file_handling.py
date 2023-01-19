import pickle
from datetime import date

from config import PROJECT_ROOT, AV_TESTING_APPROACH


def dump_default_violation_results_by_pickle(default_violation_results_list):
    with open(default_violation_dump_data_path, 'wb') as f:
        pickle.dump(default_violation_results_list, f, protocol=4)


def load_default_violation_results_by_pickle(default_violation_load_data_path):
    default_violation_results_list = pickle.load(open(default_violation_load_data_path, 'rb'))
    return default_violation_results_list


time_str = str(date.today())

# base_path = f"{PROJECT_ROOT}/data/exp_results/{AV_TESTING_APPROACH}/{time_str}"
base_path = f"{PROJECT_ROOT}/data/exp_results/DoppelTest/2023-01-16"

default_violation_load_data_path = f"{base_path}/default_violation_pickle"
default_violation_dump_data_path = f"{base_path}/default_violation_pickle_dump"

default_violation_results_list = load_default_violation_results_by_pickle(default_violation_load_data_path)

print(default_violation_results_list)

# new_list =[]
# for default_list in default_violation_results_list:
#     alist = [item for item in default_list if item[0]!='module']
#     new_list.append(alist)
#
#
# dump_default_violation_results_by_pickle(new_list)
