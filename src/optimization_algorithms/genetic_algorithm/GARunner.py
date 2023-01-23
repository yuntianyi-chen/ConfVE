import random
import time
from config import GENERATION_LIMIT, INIT_POP_SIZE
from optimization_algorithms.TestRunner import TestRunner
from optimization_algorithms.genetic_algorithm.ga import crossover, select, mutation, generate_individuals, mutate
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.run_scenarios import run_scenarios, check_default_running


class GARunner(TestRunner):
    def __init__(self, containers):
        super().__init__(containers)
        self.ga_runner()


    def ga_runner(self):
        start_time = time.time()


        init_individual_list = generate_individuals(self.config_file_obj, INIT_POP_SIZE)

        # initial mutation
        individual_list = mutate(init_individual_list, self.config_file_obj, self.range_analyzer)

        ind_list = []
        for generation_num in range(GENERATION_LIMIT):
            print("-------------------------------------------------")
            print(f"Generation_{generation_num}")
            print("-------------------------------------------------")

            self.file_output_manager.delete_data_core()

            individual_list_after_crossover = crossover(individual_list)
            individual_list_after_mutate = mutation(individual_list_after_crossover, self.config_file_obj, self.range_analyzer)

            individual_num = 0
            for generated_individual in individual_list_after_mutate:
                generated_individual.reset_default()
                print("-------------------------------------------------")
                gen_ind_id = f"Generation_{str(generation_num)}_Config_{individual_num}"
                print(gen_ind_id)
                self.file_output_manager.report_tuning_situation(generated_individual, self.config_file_obj)

                # if generated_individual.fitness == 0:
                generated_individual.update_id(gen_ind_id)

                # scenario refers to a config setting with different fixed obstacles, traffic lights(if existing), and adc routes
                scenario_list = create_scenarios(generated_individual, self.config_file_obj,
                                                 self.message_generator.pre_record_info_list,
                                                 name_prefix=gen_ind_id)

                # test each config settings under several groups of obstacles and adc routes
                run_scenarios(generated_individual, scenario_list, self.containers)

                generated_individual.calculate_fitness()
                self.check_scenario_list_vio_emergence(scenario_list)

                ind_list.append(generated_individual)

                self.file_output_manager.print_violation_results(generated_individual)
                self.file_output_manager.save_total_violation_results(generated_individual, scenario_list)
                self.file_output_manager.handle_scenario_record(scenario_list)

                if generated_individual.fitness > 0:

                    if generated_individual.option_tuning_tracking_list:
                        option_tuning_item = generated_individual.option_tuning_tracking_list[-1]
                    else:
                        option_tuning_item = "default"

                    range_change_str = self.range_analyzer.range_analyze(option_tuning_item, self.config_file_obj)
                    self.file_output_manager.save_config_file(gen_ind_id)
                    self.file_output_manager.save_fitness_result(generated_individual, gen_ind_id)

                    self.file_output_manager.save_vio_features(generated_individual, scenario_list)
                    # file_output_manager.save_emerged_violation_stats(generated_individual, scenario_list)

                    self.file_output_manager.save_option_tuning_file(
                        generated_individual,
                        gen_ind_id,
                        option_tuning_item,
                        range_change_str
                    )
                    self.file_output_manager.save_count_dict_file()
                    # revert configuration after detecting violations
                    # generated_individual.configuration_reverting(do_reverting=CONFIGURATION_REVERTING)

                individual_num += 1

            random.shuffle(individual_list_after_mutate)
            # Fitness the more, the better, currently, for testing
            individual_list_after_mutate.sort(reverse=True, key=lambda x: x.fitness)
            individual_list = select(individual_list_after_mutate, self.config_file_obj)
            # output range analysis every generation
            self.file_output_manager.update_range_analysis_file(self.config_file_obj, self.range_analyzer, generation_num)

            self.message_generator.replace_records(self.scenario_rid_emergence_list)
            check_default_running(self.message_generator, self.config_file_obj, self.file_output_manager, self.containers)
            self.scenario_rid_emergence_list = []

        end_time = time.time()
        print("Time cost: " + str((end_time - start_time) / 3600) + " hours")
        self.file_output_manager.dump_individual_by_pickle(ind_list)

    # def check_scenario_list_vio_emergence(self, scenario_list):
    #     for scenario in scenario_list:
    #         if not scenario.has_emerged_module_violations:
    #             if scenario.record_id not in self.scenario_rid_emergence_list:
    #                 self.scenario_rid_emergence_list.append(scenario.record_id)
