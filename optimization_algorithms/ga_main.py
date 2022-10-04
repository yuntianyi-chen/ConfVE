import os
import random
import shutil

from config import APOLLO_ROOT, MAGGIE_ROOT
from cyber_env.cyber_env_operation import cyber_env_init
from objectives.violation_number.oracles import RecordAnalyzer
from optimization_algorithms.genetic_algorithm.ga import ga_init, crossover, mutate, calculate_fitness, select
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.run_scenario import run_scenarios, replay_scenario
from tools.config_file_handler.parser_apollo import parser2class
from tools.config_file_handler.translator_apollo import option_obj_translator, save2file


def measure_code_coverage():
    return


def measure_execution_time():
    return


def measure_violation_number(record_path):
    ra = RecordAnalyzer(record_path)
    ra.analyze()
    return


def measure_objectives(scenario_list):
    shutil.rmtree(f"{MAGGIE_ROOT}/data/records")
    shutil.copytree(f"{APOLLO_ROOT}/records", f"{MAGGIE_ROOT}/data/records")
    # record_path =
    # cmd = f"docker exec -d {get_container_name()} cyber_recorder record -o {RECORDS_DIR}/{self.record_name} -a &"
    for scenario in scenario_list:
        record_path = scenario.record_name
        violation_number = measure_violation_number(record_path)
        replay_scenario(record_path)
        code_coverage = measure_code_coverage()
        execution_time = measure_execution_time()
        return violation_number, code_coverage, execution_time


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
            print(f"Generation {generation_num}_Individual {individual_num}")

            if generated_individual.fitness is None:
                # scenario refers to a config setting with different fixed obstacles and adc routes
                scenario_list = create_scenarios(generated_individual, option_obj_list, generation_num, individual_num)

                # test each config settings under several groups of obstacles and adc routes
                run_scenarios(scenario_list, bridge)

                violation_number, code_coverage, execution_time = measure_objectives(scenario_list)

                fitness = calculate_fitness(violation_number, code_coverage, execution_time)

                generated_individual.fitness = fitness
                individual_num += 1

        random.shuffle(individual_list_after_mutate)
        individual_list_after_mutate.sort(key=lambda x: x.fitness)
        individual_list = select(individual_list_after_mutate, option_obj_list)


if __name__ == '__main__':
    module_config_path = "./configuration_files/Apollo/test_planning_config.pb.txt"
    ga_main(module_config_path)
