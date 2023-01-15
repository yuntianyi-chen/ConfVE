import os
import random
import time
from config import APOLLO_RECORDS_DIR, INITIAL_SCENARIO_RECORD_DIR, DEFAULT_CONFIG_FILE_PATH, GENERATION_LIMIT, INIT_POP_SIZE
from config_file_handler.parser_apollo import config_file_parser2obj
from environment.MapLoader import MapLoader
from optimization_algorithms.genetic_algorithm.ga import crossover, select, mutation, generate_individuals, mutate
from range_analysis.RangeAnalyzer import RangeAnalyzer
from scenario_handling.FileOutputManager import FileOutputManager
from scenario_handling.MessageGenerator import MessageGenerator
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.MessageHandler import MessageHandler
from scenario_handling.run_scenarios import run_scenarios, check_default_running


class GARunner:
    def __init__(self):
        MapLoader()
        self.ga_runner()

    def ga_runner(self):
        start_time = time.time()

        config_file_obj = config_file_parser2obj(DEFAULT_CONFIG_FILE_PATH)
        range_analyzer = RangeAnalyzer(config_file_obj)
        file_output_manager = FileOutputManager()
        file_output_manager.delete_dir(dir_path=APOLLO_RECORDS_DIR, mk_dir=True)
        message_handler = MessageHandler()

        print("Initial Scenario Violation Info:")
        initial_record_info = MessageGenerator().get_record_info_by_approach(scenario_record_dir_path=INITIAL_SCENARIO_RECORD_DIR)

        if os.path.exists(file_output_manager.default_violation_dump_data_path):
            default_violation_results_list = file_output_manager.load_default_violation_results_by_pickle()
        else:
            default_violation_results_list = check_default_running(initial_record_info, config_file_obj,
                                                                   file_output_manager, message_handler)

        print("Default Config Rerun - Initial Scenario Violation Info:")

        pre_record_info = initial_record_info.update(default_violation_results_list)

        init_individual_list = generate_individuals(config_file_obj, INIT_POP_SIZE)

        # initial mutation
        individual_list = mutate(init_individual_list, config_file_obj, range_analyzer)

        ind_list = []
        for generation_num in range(GENERATION_LIMIT):
            print("-------------------------------------------------")
            print(f"Generation_{generation_num}")
            print("-------------------------------------------------")

            file_output_manager.delete_data_core()

            individual_list_after_crossover = crossover(individual_list)
            individual_list_after_mutate = mutation(individual_list_after_crossover, config_file_obj, range_analyzer)

            individual_num = 0
            for generated_individual in individual_list_after_mutate:
                print("-------------------------------------------------")
                gen_ind_id = f"Generation_{str(generation_num)}_Config_{individual_num}"
                print(gen_ind_id)
                file_output_manager.report_tuning_situation(generated_individual, config_file_obj)

                if generated_individual.fitness == 0:
                    generated_individual.update_id(gen_ind_id)

                    # scenario refers to a config setting with different fixed obstacles, traffic lights(if existing), and adc routes
                    scenario_list = create_scenarios(generated_individual, config_file_obj, pre_record_info,
                                                     name_prefix=gen_ind_id)

                    # test each config settings under several groups of obstacles and adc routes
                    run_scenarios(generated_individual, scenario_list, message_handler, is_default_running=False)

                    generated_individual.calculate_fitness()

                    ind_list.append(generated_individual)

                    file_output_manager.print_violation_results(generated_individual)
                    file_output_manager.save_total_violation_results(generated_individual, scenario_list)
                    file_output_manager.handle_scenario_record(scenario_list)

                    if generated_individual.fitness > 0:
                        if generated_individual.option_tuning_tracking_list:
                            option_tuning_item = generated_individual.option_tuning_tracking_list[-1]
                        else:
                            option_tuning_item = "default"

                        range_change_str = range_analyzer.range_analyze(option_tuning_item, config_file_obj)
                        file_output_manager.save_config_file(gen_ind_id)
                        file_output_manager.save_fitness_result(generated_individual, gen_ind_id)
                        file_output_manager.save_emerged_violation_stats(generated_individual, scenario_list)
                        file_output_manager.save_option_tuning_file(generated_individual, gen_ind_id,
                                                                    option_tuning_item,
                                                                    range_change_str)
                        file_output_manager.save_count_dict_file()
                        # revert configuration after detecting violations
                        # generated_individual.configuration_reverting(do_reverting=CONFIGURATION_REVERTING)

                    individual_num += 1

            random.shuffle(individual_list_after_mutate)
            # Fitness the more, the better, currently, for testing
            individual_list_after_mutate.sort(reverse=True, key=lambda x: x.fitness)
            individual_list = select(individual_list_after_mutate, config_file_obj)
            # output range analysis every generation
            file_output_manager.update_range_analysis_file(config_file_obj, range_analyzer, generation_num)

        end_time = time.time()
        print("Time cost: " + str((end_time - start_time) / 3600) + " hours")
        file_output_manager.dump_individual_by_pickle(ind_list)
