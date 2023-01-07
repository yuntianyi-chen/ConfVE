import glob
import os
import pickle
import random
import shutil
import time
from datetime import date
from config import MODULE_NAME, FITNESS_MODE, ENABLE_CROSSOVER, CONFIGURATION_REVERTING, CONFIG_FILE_PATH, \
    BACKUP_CONFIG_SAVE_PATH
from environment.cyber_env_operation import cyber_env_init, delete_records, connect_bridge, delete_data_core
from optimization_algorithms.genetic_algorithm.ga import ga_init, crossover, select, file_init, mutation, \
    initial_mutation
from range_analysis.range_analysis import generate_new_range
from range_analysis.tuning_option_item import OptionTuningItem
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.run_scenario import run_scenarios
from testing_approaches.interface import get_record_info_by_approach
from tools.config_file_handler.parser_apollo import parser2class


def ga_main(module_config_path):
    raw_option_stack, option_tuple_list, option_obj_list, option_num = parser2class(module_config_path)

    init_individual_list, generation_limit, option_type_list, range_list, default_option_value_list = ga_init(
        option_obj_list)

    # initial mutation
    individual_list = initial_mutation(init_individual_list, option_type_list, option_obj_list, range_list)

    delete_records()

    start_time = time.time()

    # obstacle_chromosomes_list = init_obs()

    optimal_fitness = 0
    ind_list = []

    time_str = str(date.today())
    violation_save_file_path, ind_fitness_save_file_path, option_tuning_file_path, ind_list_pickle_dump_data_path = file_init(time_str)


    for generation_num in range(generation_limit):
        print("-------------------------------------------------")
        print(f"Generation_{generation_num}")
        print("-------------------------------------------------")
        # cyber_env_init()
        bridge = connect_bridge()
        delete_data_core()

        if ENABLE_CROSSOVER:
            individual_list_after_crossover = crossover(individual_list)
            individual_list_after_mutate = mutation(individual_list_after_crossover, option_type_list, option_obj_list,
                                                    range_list)
        else:
            individual_list_after_mutate = mutation(individual_list, option_type_list, option_obj_list, range_list)

        individual_num = 0

        pre_record_info = get_record_info_by_approach()

        for generated_individual in individual_list_after_mutate:
            print("-------------------------------------------------")
            gen_ind_id = f"Generation_{str(generation_num)}_Config_{individual_num}"
            print(gen_ind_id)

            report_tuning_situation(generated_individual.value_list, default_option_value_list, option_obj_list)

            # Restart cyber_env to fix the image static bug here
            cyber_env_init()
            if generated_individual.fitness == 0:
                generated_individual.update_id(gen_ind_id)

                # scenario refers to a config setting with different fixed obstacles and adc routes
                scenario_list = create_scenarios(generated_individual, option_obj_list, generation_num, individual_num,
                                                 pre_record_info)

                # test each config settings under several groups of obstacles and adc routes
                run_scenarios(generated_individual, scenario_list, bridge, violation_save_file_path)

                generated_individual.calculate_fitness(FITNESS_MODE)

                ##############
                print(f" Vio Emerged Num: {generated_individual.violation_intro}")
                print(f" Vio Emerged Results: {generated_individual.violations_emerged_results}")
                # print(f" Vio Removed Num: {generated_individual.violation_remov}")
                # print(f" Vio Removed Results: {generated_individual.violations_removed_results}")
                # print(f" Fitness(mode: {FITNESS_MODE}): {generated_individual.fitness}")
                ##############

                ind_list.append(generated_individual)

                # write report
                if generated_individual.fitness >= optimal_fitness and generated_individual.fitness > 0:
                    with open(ind_fitness_save_file_path, "a") as f:
                        f.write(f"{gen_ind_id}\n")
                        f.write(f"  Vio Intro: {generated_individual.violation_intro}\n")
                        f.write(f"  Vio Remov: {generated_individual.violation_remov}\n")
                        f.write(f"  Fitness(mode: {FITNESS_MODE}): {generated_individual.fitness}\n")
                    optimal_fitness = generated_individual.fitness
                else:
                    for scenario in scenario_list:
                        scenario.delete_record()

                if generated_individual.violation_intro > 0:
                    option_tuning_item = generated_individual.option_tuning_tracking_list[-1]

                    # report option tuning
                    with open(option_tuning_file_path, "a") as f:
                        f.write(f"{gen_ind_id}\n")
                        f.write(f"  Option Tuning: {option_tuning_item}\n")
                        f.write(f"  Violation Emergence Num: {len(generated_individual.violations_emerged_results)}\n")
                        f.write(f"  Violation: {generated_individual.violations_emerged_results}\n")

                        # range analysis
                        # if pre non-violated, this time violated
                        if isinstance(option_tuning_item, OptionTuningItem):
                            cur_range = range_list[option_tuning_item.position]
                            new_range = generate_new_range(cur_range, option_tuning_item, default_option_value_list)
                            range_list[option_tuning_item.position] = new_range
                            f.write(f"  Range Change: {option_tuning_item.position}, {option_tuning_item.option_key}, {cur_range}->{new_range}\n")

                            # print(f"  Range: {option_tuning_item.position}, {option_tuning_item.option_key}, {cur_range}->{new_range}")

                    # save config file
                    config_file_save_path = f"{BACKUP_CONFIG_SAVE_PATH}/{time_str}/{gen_ind_id}"
                    if not os.path.exists(config_file_save_path):
                        os.makedirs(config_file_save_path)
                    shutil.copy(CONFIG_FILE_PATH, f"{config_file_save_path}/{MODULE_NAME}_config.pb.txt")

                    # revert configuration after detecting violations
                    generated_individual.configuration_reverting(do_reverting=CONFIGURATION_REVERTING)

                individual_num += 1

        random.shuffle(individual_list_after_mutate)

        # Fitness the more, the better, currently, for testing
        individual_list_after_mutate.sort(reverse=True, key=lambda x: x.fitness)
        individual_list = select(individual_list_after_mutate, option_obj_list)

    end_time = time.time()
    print("Time cost: " + str((end_time - start_time) / 3600) + " hours")
    ind_list.sort(reverse=True, key=lambda x: x.fitness)

    with open(ind_list_pickle_dump_data_path, 'wb') as f:
        pickle.dump(ind_list, f, protocol=4)


def report_tuning_situation(cur_value_list, default_value_list, option_obj_list):
    # diff_list = []
    print("Report Tuning...")
    for i in range(len(default_value_list)):
        if cur_value_list[i] != default_value_list[i]:
            option_obj = option_obj_list[i]
            # diff_list.append()
            print(f"  {option_obj.option_id}, {option_obj.option_key}, {default_value_list[i]}->{cur_value_list[i]}")


if __name__ == '__main__':
    # module_config_path = f"{APOLLO_ROOT}/modules/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
    # module_config_path = f"../data/config_files/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
    module_name = "control"

    conf_files_path = glob.glob(
        f"C:\\Projects\\Research\\Autonomous Vehicles\\apollo\\apollo\\modules\\{module_name}\\conf" + '/**/calibration_table.pb.txt',
        recursive=True)

    # conf_files_path = glob.glob(
    #     f"C:\\Projects\\Research\\Autonomous Vehicles\\apollo\\apollo\\modules\\{module_name}\\conf" + '/**/*_conf.pb.txt',
    #     recursive=True)
    # config_files_path = glob.glob(
    #     f"C:\\Projects\\Research\\Autonomous Vehicles\\apollo\\apollo\\modules\\{module_name}\\conf" + '/**/*_config.pb.txt',
    #     recursive=True)
    all_config_files_path = conf_files_path
    type_stat_dict = {}
    print(len(all_config_files_path))
    for config_file in all_config_files_path:
        # if "calibration" in config_file:
        # ga_main(module_config_path)
        print(config_file)
        raw_option_stack, option_tuple_list, option_obj_list, option_num = parser2class(config_file)

        init_individual_list, generation_limit, option_type_list = ga_init(option_obj_list)

        for i in option_type_list:
            if i not in type_stat_dict.keys():
                type_stat_dict[i] = 1
            else:
                type_stat_dict[i] += 1

    print(type_stat_dict)
    print(sum(type_stat_dict.values()))
