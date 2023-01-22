from config import DEFAULT_DETERMINISM_RERUN_TIMES, MODULE_ORACLES
from duplicate_elimination.ViolationChecker import check_emerged_violations, confirm_determinism
from objectives.measure_objectives import measure_objectives_individually
from optimization_algorithms.genetic_algorithm.ga import generate_individuals
from scenario_handling.ScenarioRunner import run_scenarios_by_division
from scenario_handling.create_scenarios import create_scenarios
from config import DETERMINISM_RERUN_TIMES






def run_default_scenarios(generated_individual, scenario_list, containers):
    for scenario in scenario_list:
        # if module failure happens when default running, please rerun the program
        _, all_emerged_results = confirm_determinism(scenario, containers, rerun_times=DEFAULT_DETERMINISM_RERUN_TIMES)
        print(f"Default Violations:{all_emerged_results}")
        generated_individual.violations_emerged_results_list.append((scenario.record_id, all_emerged_results))


def run_scenarios(generated_individual, scenario_list, containers):
    print("Normal Run...")

    run_scenarios_by_division(scenario_list, containers)

    for scenario in scenario_list:
        objectives = measure_objectives_individually(scenario)
        violations_emerged_results = check_emerged_violations(objectives.violation_results, scenario.original_violation_results)

        contain_module_violation = check_module_failure(violations_emerged_results)

        # if bug-revealing (module failure), confirm determinism
        # if len(violations_emerged_results) > 0 and generated_individual.allow_selection:

        # once found module failure, don't need to check determinism of other scenarios
        if contain_module_violation and generated_individual.allow_selection:
            violations_emerged_results, _ = confirm_determinism(scenario, containers, rerun_times=DETERMINISM_RERUN_TIMES)

            contain_module_violation = check_module_failure(violations_emerged_results)

            generated_individual.update_allow_selection(contain_module_violation)

        scenario.update_emerged_status(violations_emerged_results, contain_module_violation)
        generated_individual.update_violation_emerged_with_sid(violations_emerged_results, scenario)
        generated_individual.update_accumulated_objectives(objectives)


def check_module_failure(violations_emerged_results):
    for emerged_violation in violations_emerged_results:
        if emerged_violation.main_type in MODULE_ORACLES:
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
    default_individual = generate_individuals(config_file_obj, population_size=1)[0]
    name_prefix = "default"
    file_output_manager.output_initial_record2default_mapping(message_generator.pre_record_info_list, name_prefix)

    selected_pre_record_info_list = message_generator.get_not_rerun_record()

    scenario_list = create_scenarios(default_individual, config_file_obj, selected_pre_record_info_list, name_prefix)

    run_default_scenarios(default_individual, scenario_list, containers)
    file_output_manager.save_default_scenarios()

    message_generator.update_rerun_status()

    default_violation_results_list = default_individual.violations_emerged_results_list

    file_output_manager.dump_default_violation_results_by_pickle(default_violation_results_list)

    message_generator.update_selected_records_violatioin_directly(default_violation_results_list)

    # return default_violation_results_list





