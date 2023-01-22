from copy import deepcopy
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from config import MODULE_ORACLES, SIMILARITY_THRESHOLD, DETERMINISM_CONFIRMED_TIMES
from objectives.measure_objectives import measure_objectives_individually
from scenario_handling.ScenarioRunner import run_scenarios_by_division


# class ViolationChecker:
#
#     def __init__(self):
#         return
##################################

# def check_emerged_violations(violation_results, scenario):
#     violations_emerged_results = []
#     violations_removed_results = []
#     for violation in violation_results:
#         if violation not in scenario.original_violation_results:
#             violations_emerged_results.append(violation)
#     for violation in scenario.original_violation_results:
#         if violation not in violation_results:
#             violations_removed_results.append(violation)
#     return violations_emerged_results, violations_removed_results


def calculate_similarity(features, default_features):
    p_corr, _ = pearsonr(features, default_features)
    # s_corr, _ = spearmanr(features, default_features)
    # k_corr, _ = kendalltau(features, default_features)
    # dst = distance.euclidean(features, default_features)
    # aa=np.corrcoef(features, default_features)
    return p_corr


def compare_similarity(features, default_features_list):
    pd_default_features = pd.DataFrame(default_features_list)
    pd_all_features = pd_default_features.append(features, ignore_index=True)

    # scaler = MinMaxScaler()
    scaler = StandardScaler()

    pd_all_features_scaled = scaler.fit_transform(pd_all_features)

    pd_default_features_scaled = pd_all_features_scaled[:-1]
    pd_features_scaled = pd_all_features_scaled[-1]

    check_similar = False
    # not similar with any violation in default list
    for pd_default_features_scaled_item in pd_default_features_scaled:
        corr = calculate_similarity(pd_features_scaled, pd_default_features_scaled_item)
        # corr_list.append(corr)
        if corr >= SIMILARITY_THRESHOLD:
            check_similar = True
            break
    return check_similar


def check_emerged_violations(violation_results, default_violations_results):
    violations_emerged_results = []
    for violation in violation_results:
        if violation.main_type in MODULE_ORACLES:
            violations_emerged_results.append(violation)
        else:
            default_features_list = [d.features for d in default_violations_results if
                                     d.main_type == violation.main_type]
            if not default_features_list:
                violations_emerged_results.append(violation)
            else:
                check_similar = compare_similarity(violation.features, default_features_list)
                if not check_similar:
                    violations_emerged_results.append(violation)
    return violations_emerged_results



def confirm_determinism(scenario, containers, rerun_times):
    for container in containers:
        container.cyber_env_init()

    rerun_scenario_list = []
    for i in range(rerun_times):
        temp_scenario = deepcopy(scenario)
        temp_record_name = f"{temp_scenario.record_name}_rerun_{i}"
        temp_scenario.update_record_name_and_path(temp_record_name)
        scenario.confirmed_record_name_list.append(temp_record_name)
        rerun_scenario_list.append(temp_scenario)

    print("Rerun...")

    run_scenarios_by_division(rerun_scenario_list, containers)

    accumulated_emerged_results_count_dict = {}
    all_emerged_results = []

    for temp_scenario in rerun_scenario_list:
        # print(f"Scenario_{temp_scenario.scenario_id}")
        objectives = measure_objectives_individually(temp_scenario)

        violations_emerged_results = check_emerged_violations(objectives.violation_results, temp_scenario.original_violation_results)

        for emerged_violation in violations_emerged_results:
            if emerged_violation.main_type not in accumulated_emerged_results_count_dict.keys():
                accumulated_emerged_results_count_dict[emerged_violation.main_type] = [emerged_violation]
            else:
                accumulated_emerged_results_count_dict[emerged_violation.main_type].append(emerged_violation)

        for violation in objectives.violation_results:
            if violation not in all_emerged_results:
                all_emerged_results.append(violation)

    determined_emerged_results = [v[0] for v in accumulated_emerged_results_count_dict.values() if
                                  len(v) >= DETERMINISM_CONFIRMED_TIMES]

    return determined_emerged_results, all_emerged_results
