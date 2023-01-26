import time
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.ScenarioRunner import run_scenarios_by_division
from optimization_algorithms.genetic_algorithm.ga import generate_individuals
from duplicate_elimination.ViolationChecker import check_emerged_violations, confirm_determinism
from config import DEFAULT_DETERMINISM_RERUN_TIMES, MODULE_ORACLES, DETERMINISM_RERUN_TIMES


def run_default_scenarios(scenario_list, containers):
    default_violation_results_list = []
    for scenario in scenario_list:
        # if module failure happens when default running, rerun the program
        all_emerged_results = []
        contain_module_violation = True
        while contain_module_violation:
            _, all_emerged_results = confirm_determinism(scenario, containers,
                                                         rerun_times=DEFAULT_DETERMINISM_RERUN_TIMES)
            contain_module_violation = check_module_failure(all_emerged_results, oracles=MODULE_ORACLES)
        print(f"Default Violations:{all_emerged_results}")
        print("-------------------------------------------------")
        default_violation_results_list.append((scenario.record_id, all_emerged_results))
    return default_violation_results_list


def run_scenarios(generated_individual, scenario_list, containers):
    print("Normal Run...")
    start_time = time.time()
    run_scenarios_by_division(scenario_list, containers)

    for scenario in scenario_list:
        violation_results = scenario.measure_violations()
        violations_emerged_results = check_emerged_violations(violation_results, scenario.original_violation_results)
        contain_module_violation = check_module_failure(violations_emerged_results, oracles=MODULE_ORACLES[:-1])

        # if bug-revealing (module failure), confirm determinism
        # if len(violations_emerged_results) > 0 and generated_individual.allow_selection:
        # once found module failure, don't need to check determinism of other scenarios

        determinism_start_time = time.time()
        if contain_module_violation and generated_individual.allow_selection:
            violations_emerged_results, _ = confirm_determinism(scenario, containers, rerun_times=DETERMINISM_RERUN_TIMES)
            contain_module_violation = check_module_failure(violations_emerged_results, oracles=MODULE_ORACLES[:-1])
            generated_individual.update_allow_selection(contain_module_violation)
        determinism_time = time.time() - determinism_start_time
        start_time = start_time + determinism_time

        scenario.update_emerged_status(violations_emerged_results, contain_module_violation)
        generated_individual.update_violation_result(violations_emerged_results, violation_results, scenario)

    total_time = time.time() - start_time
    generated_individual.update_exec_time(total_time)


def check_module_failure(violations_emerged_results, oracles):
    for emerged_violation in violations_emerged_results:
        if emerged_violation.main_type in oracles:
            print(f"    Contain module violation: {emerged_violation.main_type}")
            return True
    return False


def check_emerged_violations_for_tuple(violation_results, scenario):
    violations_emerged_results = []
    violations_removed_results = []
    for violation in violation_results:
        if violation not in scenario.original_violation_results:
            violations_emerged_results.append(violation)
    for violation in scenario.original_violation_results:
        if violation not in violation_results:
            violations_removed_results.append(violation)
    return violations_emerged_results, violations_removed_results


def check_default_running(message_generator, config_file_obj, file_output_manager, containers):
    selected_pre_record_info_list = message_generator.get_not_rerun_record()
    default_violation_results_list = []
    if selected_pre_record_info_list:
        name_prefix = "default"

        file_output_manager.output_initial_record2default_mapping(message_generator.pre_record_info_list, name_prefix)

        default_individual = generate_individuals(config_file_obj, population_size=1)[0]

        scenario_list = create_scenarios(default_individual, config_file_obj, selected_pre_record_info_list,
                                         name_prefix)

        default_violation_results_list = run_default_scenarios(scenario_list, containers)

        file_output_manager.save_default_scenarios()
        message_generator.update_rerun_status()

        message_generator.update_selected_records_violatioin_directly(default_violation_results_list)

    return default_violation_results_list
