import random
from environment.cyber_env_operation import cyber_env_init
from optimization_algorithms.genetic_algorithm.ga import ga_init, crossover, mutate, select
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.run_scenario import run_scenarios, replay_scenario
from tools.config_file_handler.parser_apollo import parser2class


def ga_main(module_config_path):
    raw_option_stack, option_tuple_list, option_obj_list, option_num = parser2class(module_config_path)

    init_individual_list, generation_limit, option_type_list = ga_init(option_obj_list)

    individual_list = init_individual_list

    bridge = cyber_env_init()
    for generation_num in range(generation_limit):
        individual_list_after_crossover = crossover(individual_list)
        individual_list_after_mutate = mutate(individual_list_after_crossover, option_type_list)

        individual_num = 0
        for generated_individual in individual_list_after_mutate:
            print("-------------------------------------------------")
            print(f"Generation_{generation_num} Individual_{individual_num}")

            if generated_individual.fitness is None:
                # scenario refers to a config setting with different fixed obstacles and adc routes
                scenario_list = create_scenarios(generated_individual, option_obj_list, generation_num, individual_num)

                # test each config settings under several groups of obstacles and adc routes
                run_scenarios(scenario_list, bridge)

                # violation_number, code_coverage, execution_time = measure_objectives(scenario_list)

                # fitness = calculate_fitness(violation_number, code_coverage, execution_time)

                # generated_individual.fitness = fitness
                individual_num += 1

        random.shuffle(individual_list_after_mutate)
        individual_list_after_mutate.sort(key=lambda x: x.fitness)
        individual_list = select(individual_list_after_mutate, option_obj_list)



# if __name__ == '__main__':
    # shutil.rmtree(f"{MAGGIE_ROOT}/data/records")
    # shutil.copytree(f"{APOLLO_ROOT}/records", f"{MAGGIE_ROOT}/data/records")
    # init_settings()
    # list_a=os.listdir(f"{MAGGIE_ROOT}/data/records")
    # # list_a.sort(reverse=True)
    # list_a.sort()
    #
    # for record_name in list_a:
    #     record_path = f"{RECORDS_DIR}/{record_name}"
    #     violation_number = measure_violation_number(record_path)
    #     replay_scenario(record_path)
    #     code_coverage = measure_code_coverage()
    #     execution_time = measure_execution_time()
    #     print()