import time
from config import GENERATION_LIMIT, INIT_POP_SIZE, TIME_HOUR_THRESHOLD
from optimization_algorithms.TestRunner import TestRunner
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.run_scenarios import run_scenarios, check_default_running
from optimization_algorithms.genetic_algorithm.ga import crossover, select, mutation, generate_individuals, mutate


class GARunner(TestRunner):
    def __init__(self, containers):
        super().__init__(containers)
        self.ga_runner()

    def ga_runner(self):
        # print("Start GA")

        init_individual_list = generate_individuals(self.config_file_obj, INIT_POP_SIZE)

        # initial mutation
        individual_list = mutate(init_individual_list, self.config_file_obj, self.range_analyzer)

        # ind_list = []
        for generation_num in range(GENERATION_LIMIT):
            print("-------------------------------------------------")
            print(f"Generation_{generation_num}")
            print("-------------------------------------------------")

            individual_list_after_crossover = crossover(individual_list)
            individual_list_after_mutate = mutation(individual_list_after_crossover, self.config_file_obj,
                                                    self.range_analyzer)

            individual_num = 0
            for generated_individual in individual_list_after_mutate:
                self.file_output_manager.delete_temp_files()

                generated_individual.reset_default()

                print("-------------------------------------------------")
                ind_id = f"Generation_{str(generation_num)}_Config_{individual_num}"
                print(ind_id)
                self.file_output_manager.report_tuning_situation(generated_individual, self.config_file_obj)

                generated_individual.update_id(ind_id)

                # scenario refers to a config setting with different fixed obstacles, traffic lights(if existing), and adc routes
                scenario_list = create_scenarios(generated_individual, self.config_file_obj,
                                                 self.message_generator.pre_record_info_list,
                                                 name_prefix=ind_id)

                # test each config settings under several groups of obstacles and adc routes
                run_scenarios(generated_individual, scenario_list, self.containers)

                generated_individual.update_fitness()

                self.check_scenario_list_vio_emergence(scenario_list)
                self.file_output_manager.print_violation_results(generated_individual)
                self.file_output_manager.save_total_violation_results(generated_individual, scenario_list)
                self.file_output_manager.handle_scenario_record(scenario_list)

                if len(generated_individual.violations_emerged_results) > 0:
                    if generated_individual.option_tuning_tracking_list:
                        option_tuning_item = generated_individual.option_tuning_tracking_list[-1]
                    else:
                        option_tuning_item = "default"

                    range_change_str = self.range_analyzer.range_analyze(option_tuning_item, self.config_file_obj)
                    self.file_output_manager.save_config_file(ind_id)
                    # self.file_output_manager.save_fitness_result(generated_individual, ind_id)
                    self.file_output_manager.save_vio_features(generated_individual, scenario_list)
                    self.file_output_manager.save_option_tuning_file(generated_individual, ind_id, option_tuning_item,
                                                                     range_change_str)
                    self.file_output_manager.save_count_dict_file()

                individual_num += 1

                if time.time() - self.runner_time >= TIME_HOUR_THRESHOLD * 3600:
                    return

            filtered_individual_list = [item for item in individual_list_after_mutate if item.allow_selection]
            individual_list = select(filtered_individual_list, self.config_file_obj)

            # output range analysis every generation
            self.file_output_manager.update_range_analysis_file(self.config_file_obj, self.range_analyzer,
                                                                generation_num)

            self.message_generator.replace_records(self.scenario_rid_emergence_list)
            _ = check_default_running(self.message_generator, self.config_file_obj, self.file_output_manager,
                                      self.containers)
            self.scenario_rid_emergence_list = []

        self.runner_time = time.time() - self.runner_time
        print("Time cost: " + str(self.runner_time / 3600) + " hours")
