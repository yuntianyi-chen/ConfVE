import time
from copy import deepcopy
from config import MAX_RECORD_TIME, TRAFFIC_LIGHT_MODE, DEFAULT_DETERMINISM_RERUN_TIMES
from objectives.measure_objectives import measure_objectives_individually
from optimization_algorithms.genetic_algorithm.ga import generate_individuals
from scenario_handling.create_scenarios import create_scenarios
from config import DETERMINISM_RERUN_TIMES, DETERMINISM_CONFIRMED_TIMES


def start_running(scenario, container):
    print(f"  Scenario_{scenario.scenario_id}")
    print("    Start recorder...")
    container.start_recorder(scenario.record_name)
    container.message_handler.register_obstacles_by_channel(scenario.obs_perception_messages)

    if TRAFFIC_LIGHT_MODE == "read":
        container.message_handler.register_traffic_lights_by_channel(scenario.traffic_control_msg)
    elif TRAFFIC_LIGHT_MODE == "random":
        container.message_handler.register_traffic_lights_by_channel(scenario.traffic_control_manager)

    container.message_handler.send_routing_request_by_channel(scenario.routing_request_message)

    # time.sleep(MAX_RECORD_TIME)

    # Stop recording messages and producing perception messages
    # print("    Stop recorder...")
    # container.stop_recorder()
    #
    # container.message_handler.obs_stop()
    # container.message_handler.traffic_lights_stop()


    # objectives = measure_objectives_individually(scenario)
    # violations_emerged_results, violations_removed_results = check_emerged_violations(objectives.violation_results,
    #                                                                                   scenario)
    # return violations_emerged_results, violations_removed_results, objectives

def stop_running(container):
    print("    Stop recorder...")
    container.stop_recorder()

    container.message_handler.obs_stop()
    container.message_handler.traffic_lights_stop()

def run_default_scenarios(generated_individual, scenario_list, containers):
    for container in containers:
        container.cyber_env_init()

    for scenario, container in zip(scenario_list, containers):
        # if module failure happens when default running, please rerun the program
        determined_emerged_results, all_emerged_results = confirm_determinism(scenario, container,
                                                                              rerun_times=DEFAULT_DETERMINISM_RERUN_TIMES)
        print(f"Default Violations:{all_emerged_results}")
        generated_individual.violations_emerged_results_list.append(all_emerged_results)


# def run_scenarios(generated_individual, scenario_list, message_handler):
#     # Restart cyber_env
#     cyber_env_init()
#     for scenario in scenario_list:
#
#         start_running(scenario, message_handler)
#
#         objectives = measure_objectives_individually(scenario)
#         violations_emerged_results, violations_removed_results = check_emerged_violations(objectives.violation_results,
#                                                                                           scenario)
#
#         # if bug-revealing, confirm determinism
#         # once found module failure, don't need to check determinism of other scenarios
#         if len(violations_emerged_results) > 0 and generated_individual.allow_selection:
#             determined_emerged_results, all_emerged_results = confirm_determinism(scenario, message_handler,
#                                                                                   rerun_times=DETERMINISM_RERUN_TIMES)
#             violations_emerged_results = determined_emerged_results
#
#             generated_individual.update_allow_selection(violations_emerged_results)
#             scenario.update_emerged_status(violations_emerged_results)
#
#         generated_individual.update_violation_intro_remov(violations_emerged_results, violations_removed_results,
#                                                           scenario)
#         generated_individual.update_accumulated_objectives(objectives)



def run_scenarios(generated_individual, scenario_list, containers):
    # Restart cyber_env
    # cyber_env_init()

    for container in containers:
        container.cyber_env_init()

    for scenario, container in zip(scenario_list, containers):
        start_running(scenario, container)

    time.sleep(MAX_RECORD_TIME)
    for container in containers:
        stop_running(container)


    for scenario, container in zip(scenario_list, containers):
        objectives = measure_objectives_individually(scenario)
        violations_emerged_results, violations_removed_results = check_emerged_violations(objectives.violation_results, scenario)

        # if bug-revealing, confirm determinism
        # once found module failure, don't need to check determinism of other scenarios
        if len(violations_emerged_results) > 0 and generated_individual.allow_selection:

            ### check instantly or check after analyzing all scenarios
            determined_emerged_results, all_emerged_results = confirm_determinism(scenario, container,
                                                                                  rerun_times=DETERMINISM_RERUN_TIMES)
            violations_emerged_results = determined_emerged_results

            generated_individual.update_allow_selection(violations_emerged_results)
            scenario.update_emerged_status(violations_emerged_results)

        generated_individual.update_violation_intro_remov(violations_emerged_results, violations_removed_results, scenario)
        generated_individual.update_accumulated_objectives(objectives)


def check_emerged_violations(violation_results, scenario):
    violations_emerged_results = []
    violations_removed_results = []
    for violation in violation_results:
        if violation not in scenario.original_violation_results:
            # scenario.update_emerged_status()
            # violations_emerged_results.append((scenario.scenario_id, violation))
            violations_emerged_results.append(violation)
            # self.violation_intro += 1
    for violation in scenario.original_violation_results:
        if violation not in violation_results:
            violations_removed_results.append(violation)
            # self.violation_remov += 1
    return violations_emerged_results, violations_removed_results


def check_default_running(pre_record_info, config_file_obj, file_output_manager, containers):

    default_individual = generate_individuals(config_file_obj, population_size=1)[0]
    name_prefix = "default"
    file_output_manager.output_initial_record2default_mapping(pre_record_info, name_prefix)
    scenario_list = create_scenarios(default_individual, config_file_obj, pre_record_info, name_prefix)

    run_default_scenarios(default_individual, scenario_list, containers)

    # file_output_manager.save_total_violation_results(default_individual, scenario_list)
    file_output_manager.save_default_scenarios()

    default_violation_results_list = default_individual.violations_emerged_results_list

    file_output_manager.dump_default_violation_results_by_pickle(default_violation_results_list)
    return default_violation_results_list


def confirm_determinism(scenario, container, rerun_times):
    cyber_env_init()

    accumulated_emerged_results_count_dict = {}
    all_emerged_results = []
    for i in range(rerun_times):
        temp_scenario = deepcopy(scenario)
        temp_record_name = f"{temp_scenario.record_name}_rerun_{i}"
        temp_scenario.update_record_name_and_path(temp_record_name)
        scenario.confirmed_record_name_list.append(temp_record_name)




        start_running(temp_scenario, container)
        time.sleep(MAX_RECORD_TIME)
        stop_running(container)



        objectives = measure_objectives_individually(scenario)
        violations_emerged_results, violations_removed_results = check_emerged_violations(objectives.violation_results,
                                                                                          scenario)




        for emerged_violation in violations_emerged_results:
            # emerged_violation = emerged_violation_tuple[1]
            if emerged_violation not in accumulated_emerged_results_count_dict.keys():
                accumulated_emerged_results_count_dict[emerged_violation] = 1
            else:
                accumulated_emerged_results_count_dict[emerged_violation] += 1

        for violation in objectives.violation_results:
            # violation_tuple = (scenario.scenario_id, violation)
            if violation not in all_emerged_results:
                all_emerged_results.append(violation)

    determined_emerged_results = [k for k, v in
                                  accumulated_emerged_results_count_dict.items() if
                                  v >= DETERMINISM_CONFIRMED_TIMES]


    return determined_emerged_results, all_emerged_results
    # return accumulated_emerged_results_count_dict
