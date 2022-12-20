import glob
import pickle
import random
import time
from datetime import date

from config import APOLLO_ROOT, MODULE_NAME, FITNESS_MODE, OPTIMAL_IND_LIST_LENGTH, MAGGIE_ROOT
from environment.cyber_env_operation import cyber_env_init, delete_records, connect_bridge, delete_data_core
from optimization_algorithms.genetic_algorithm.ga import ga_init, crossover, mutate, select, file_init
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.run_scenario import run_scenarios
from testing_approaches.interface import get_record_info_by_approach
from tools.config_file_handler.parser_apollo import parser2class


def ga_main(module_config_path):
    raw_option_stack, option_tuple_list, option_obj_list, option_num = parser2class(module_config_path)

    init_individual_list, generation_limit, option_type_list = ga_init(option_obj_list)

    individual_list = init_individual_list

    delete_records()

    start_time = time.time()

    # obstacle_chromosomes_list = init_obs()

    optimal_fitness = 0
    ind_list = []

    violation_save_file_path, ind_fitness_save_file_path = file_init()

    for generation_num in range(generation_limit):
        print("-------------------------------------------------")
        print(f"Generation_{generation_num}")
        print("-------------------------------------------------")
        # cyber_env_init()
        bridge = connect_bridge()
        delete_data_core()
        individual_list_after_crossover = crossover(individual_list)
        individual_list_after_mutate = mutate(individual_list_after_crossover, option_type_list)
        individual_num = 0

        ###################
        pre_record_info = get_record_info_by_approach()
        # obs_group_path_list, adc_routing_list, violation_num_list = get_record_info_by_approach()
        ###################

        for generated_individual in individual_list_after_mutate:
            print("-------------------------------------------------")
            gen_ind_id = f"Generation_{generation_num} Individual_{individual_num}"
            print(gen_ind_id)

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

                print(f" Vio Intro: {generated_individual.violation_intro}")
                print(f" Vio Remov: {generated_individual.violation_remov}")
                print(f" Fitness: {generated_individual.fitness}")

                ind_list.append(generated_individual)

                if generated_individual.fitness >= optimal_fitness:
                    with open(ind_fitness_save_file_path, "a") as f:
                        f.write(f"{gen_ind_id}\n")
                        f.write(f"  Vio Intro: {generated_individual.violation_intro}\n")
                        f.write(f"  Vio Remov: {generated_individual.violation_remov}\n")
                        f.write(f"    Fitness: {generated_individual.fitness}\n")
                    optimal_fitness = generated_individual.fitness
                else:
                    for scenario in scenario_list:
                        scenario.delete_record()

                individual_num += 1

        random.shuffle(individual_list_after_mutate)

        # Fitness the more, the better, currently, for testing
        individual_list_after_mutate.sort(reverse=True, key=lambda x: x.fitness)
        individual_list = select(individual_list_after_mutate, option_obj_list)

    end_time = time.time()
    print("Time cost: " + str((end_time - start_time) / 3600) + " hours")
    ind_list.sort(reverse=True, key=lambda x: x.fitness)

    ind_list_pickle_dump_data_path = f"{MAGGIE_ROOT}/data/pop_pickle/ind_list_{date.today()}"

    with open(ind_list_pickle_dump_data_path, 'wb') as f:
        pickle.dump(ind_list, f, protocol=4)


if __name__ == '__main__':
    # module_config_path = f"{APOLLO_ROOT}/modules/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
    # module_config_path = f"../data/config_files/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
    module_name ="control"

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
