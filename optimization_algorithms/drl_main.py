import random
import time
from config import APOLLO_ROOT, MODULE_NAME
from environment.cyber_env_operation import cyber_env_init, delete_records, connect_bridge
from optimization_algorithms.deep_reinforcement_learning.drl import drl_init, change_individuals
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.run_scenario import run_scenarios
from testing_approaches.interface import generate_obs_adc_routes_by_approach, init_obs
from tools.config_file_handler.parser_apollo import parser2class


def ga_main(module_config_path):
    raw_option_stack, option_tuple_list, option_obj_list, option_num = parser2class(module_config_path)

    init_individual_list, generation_limit, option_type_list = drl_init(option_obj_list)

    individual_list = init_individual_list

    delete_records()

    start_time = time.time()

    obstacle_chromosomes_list = init_obs()

    for generation_num in range(generation_limit):
        print("-------------------------------------------------")
        print(f"Generation_{generation_num}")
        print("-------------------------------------------------")
        bridge = connect_bridge()

        individual_list_after_change = change_individuals(individual_list, option_type_list)
        individual_num = 0

        ###################

        obs_group_path_list, adc_routing_list = generate_obs_adc_routes_by_approach(obstacle_chromosomes_list)
        ###################

        for generated_individual in individual_list_after_change:
            print("-------------------------------------------------")
            print(f"Generation_{generation_num} Individual_{individual_num}")
            # Restart cyber_env to fix the image static bug here
            cyber_env_init()
            if generated_individual.value is None:
                # scenario refers to a config setting with different fixed obstacles and adc routes
                scenario_list = create_scenarios(generated_individual, option_obj_list, generation_num, individual_num,
                                                 obs_group_path_list, adc_routing_list)

                # test each config settings under several groups of obstacles and adc routes
                run_scenarios(generated_individual, scenario_list, bridge)

                generated_individual.calculate_value()

                individual_num += 1

        random.shuffle(individual_list_after_change)

        # Fitness the more, the better, currently, for testing
        individual_list_after_change.sort(reverse=True, key=lambda x: x.value)
        ###### individual_list = select(individual_list_after_mutate, option_obj_list)

    end_time = time.time()
    print("Time cost: " + str((end_time - start_time) / 3600) + " hours")


if __name__ == '__main__':
    module_config_path = f"{APOLLO_ROOT}/modules/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
    ga_main(module_config_path)
