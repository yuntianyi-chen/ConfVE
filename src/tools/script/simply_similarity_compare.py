from config import PROJECT_ROOT, AV_TESTING_APPROACH, MAP_NAME
from duplicate_elimination.ViolationChecker import check_emerged_violations
from tools.script.pickle_file_handling import load_default_violation_results_by_pickle

base_path = f"{PROJECT_ROOT}/data/exp_results/{AV_TESTING_APPROACH}/{MAP_NAME}/2023-01-20"

default_violation_load_data_path = f"{base_path}/default_violation_pickle"
default_violation_results_list = load_default_violation_results_by_pickle(default_violation_load_data_path)

violation_results = default_violation_results_list[0]

default_violations_results = default_violation_results_list[3]
check_emerged_violations(violation_results, default_violations_results)