import os
import random
from objectives.violation_number.oracles import RecordAnalyzer
from optimization_algorithms.genetic_algorithm.ga import ga_init, crossover, mutate, calculate_fitness, select
from tools.config_file_handler.parser_apollo import parser2class
from tools.config_file_handler.translator_apollo import option_obj_translator, save2file


def run_scenario():
    record_scenario()
    return


def record_scenario():
    return


def replay_scenario(record_path):
    return


def measure_code_coverage():
    return


def measure_execution_time():
    return


def measure_violation_number(record_path):
    ra = RecordAnalyzer(record_path)
    ra.analyze()
    return


def measure_objectives(record_path):
    violation_number = measure_violation_number(record_path)
    replay_scenario(record_path)
    code_coverage = measure_code_coverage()
    execution_time = measure_execution_time()
    return violation_number, code_coverage, execution_time


def ga_main():
    # working_dir_path = "C:/Users/cloud/PycharmProjects/AV_Testing"
    # working_dir_path = "C:/Users/cloud/PycharmProjects/AV_Testing"

    # os.chdir(working_dir_path)

    raw_option_stack, option_tuple_list, option_obj_list, option_num = parser2class(
        "./configuration_files/Apollo/test_planning_config.pb.txt")

    init_individual_list, generation_limit, option_type_list = ga_init(option_obj_list)

    # init_individual_list = [IndividualWithFitness(value_list, None) for value_list in init_generated_value_lists]

    # generated_value_lists = init_generated_value_lists
    # generated_individual_list = init_individual_list

    individual_list = init_individual_list

    for i in range(generation_limit):
        individual_list_after_crossover = crossover(individual_list)
        individual_list_after_mutate = mutate(individual_list_after_crossover, option_type_list)

        for generated_individual in individual_list_after_mutate:
            if generated_individual.fitness is None:
                generated_value_list = generated_individual.value_list
                for generated_value, option_obj in zip(generated_value_list, option_obj_list):
                    option_obj.option_value = generated_value
                output_string_list = option_obj_translator(option_obj_list)
                save2file(output_string_list)

                run_scenario()

                record_path = ""
                violation_number, code_coverage, execution_time = measure_objectives(record_path)

                fitness = calculate_fitness(violation_number, code_coverage, execution_time)

                generated_individual.fitness = fitness

        random.shuffle(individual_list_after_mutate)
        individual_list_after_mutate.sort(key=lambda x: x.fitness)
        individual_list = select(individual_list_after_mutate, option_obj_list)


if __name__ == '__main__':
    ga_main()
