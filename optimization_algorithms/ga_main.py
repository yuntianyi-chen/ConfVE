import random
import time
from config import APOLLO_ROOT, MODULE_NAME
from environment.cyber_env_operation import cyber_env_init, delete_records, connect_bridge
from optimization_algorithms.genetic_algorithm.ga import ga_init, crossover, mutate, select
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.run_scenario import run_scenarios
from testing_approaches.interface import generate_obs_adc_routes_by_approach
from tools.config_file_handler.parser_apollo import parser2class


def ga_main(module_config_path):
    raw_option_stack, option_tuple_list, option_obj_list, option_num = parser2class(module_config_path)

    init_individual_list, generation_limit, option_type_list = ga_init(option_obj_list)

    individual_list = init_individual_list

    delete_records()

    start_time = time.time()

    for generation_num in range(generation_limit):
        print("-------------------------------------------------")
        print(f"Generation_{generation_num}")
        print("-------------------------------------------------")
        # cyber_env_init()
        bridge = connect_bridge()
        individual_list_after_crossover = crossover(individual_list)
        individual_list_after_mutate = mutate(individual_list_after_crossover, option_type_list)
        individual_num = 0

        ###################

        obstacle_chromosomes = []
        obs_group_path_list, adc_routing_list = generate_obs_adc_routes_by_approach(obstacle_chromosomes)
        ###################

        for generated_individual in individual_list_after_mutate:
            print("-------------------------------------------------")
            print(f"Generation_{generation_num} Individual_{individual_num}")
            # Restart cyber_env to fix the image static bug here
            cyber_env_init()
            if generated_individual.fitness is None:
                # scenario refers to a config setting with different fixed obstacles and adc routes
                scenario_list = create_scenarios(generated_individual, option_obj_list, generation_num, individual_num,
                                                 obs_group_path_list, adc_routing_list)

                # test each config settings under several groups of obstacles and adc routes
                run_scenarios(generated_individual, scenario_list, bridge)

                generated_individual.calculate_fitness()

                individual_num += 1

        random.shuffle(individual_list_after_mutate)

        # Fitness the more, the better, currently, for testing
        individual_list_after_mutate.sort(reverse=True, key=lambda x: x.fitness)
        individual_list = select(individual_list_after_mutate, option_obj_list)

    end_time = time.time()
    print("Time cost: " + str((end_time - start_time) / 3600) + " hours")


if __name__ == '__main__':
    module_config_path = f"{APOLLO_ROOT}/modules/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
    ga_main(module_config_path)
