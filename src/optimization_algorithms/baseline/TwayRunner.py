import time
from config import T_STRENGTH_VALUE, TIME_THRESHOLD
from optimization_algorithms.TestRunner import TestRunner
from optimization_algorithms.baseline.TwiseTuner import TwiseTuner
from optimization_algorithms.genetic_algorithm.ga import generate_individuals
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.run_scenarios import run_scenarios, check_default_running


class TwayRunner(TestRunner):
    def __init__(self, containers):
        super().__init__(containers)
        self.twise_tuner = TwiseTuner(self.config_file_obj, self.range_analyzer, T=T_STRENGTH_VALUE)
        self.tway_runner()

    def tway_runner(self):

        individual_num = 0
        while (self.runner_time < TIME_THRESHOLD * 3600):
            print("-------------------------------------------------")

            default_individual = generate_individuals(self.config_file_obj, population_size=1)[0]
            generated_individual = self.twise_tuner.tune_individual(default_individual)

            ind_id = f"Config_{individual_num}"
            print(ind_id)
            self.file_output_manager.report_tuning_situation(generated_individual, self.config_file_obj)

            generated_individual.update_id(ind_id)

            # scenario refers to a config setting with different fixed obstacles, traffic lights(if existing), and adc routes
            scenario_list = create_scenarios(generated_individual, self.config_file_obj,
                                             self.message_generator.pre_record_info_list,
                                             name_prefix=ind_id)

            # test each config settings under several groups of obstacles and adc routes
            run_scenarios(generated_individual, scenario_list, self.containers)

            generated_individual.calculate_fitness()
            self.check_scenario_list_vio_emergence(scenario_list)

            self.file_output_manager.print_violation_results(generated_individual)
            self.file_output_manager.save_total_violation_results(generated_individual, scenario_list)
            self.file_output_manager.handle_scenario_record(scenario_list)

            if generated_individual.fitness > 0:

                if generated_individual.option_tuning_tracking_list:
                    option_tuning_item = generated_individual.option_tuning_tracking_list[-1]
                else:
                    option_tuning_item = "default"

                range_change_str = self.range_analyzer.range_analyze(option_tuning_item, self.config_file_obj)
                self.file_output_manager.save_config_file(ind_id)
                self.file_output_manager.save_fitness_result(generated_individual, ind_id)

                self.file_output_manager.save_vio_features(generated_individual, scenario_list)

                self.file_output_manager.save_option_tuning_file(
                    generated_individual,
                    ind_id,
                    option_tuning_item,
                    range_change_str
                )
                self.file_output_manager.save_count_dict_file()

                individual_num += 1

            # self.file_output_manager.update_range_analysis_file(self.config_file_obj, self.range_analyzer, generation_num)
            self.message_generator.replace_records(self.scenario_rid_emergence_list)
            check_default_running(self.message_generator, self.config_file_obj, self.file_output_manager,
                                  self.containers)
            self.scenario_rid_emergence_list = []

            self.runner_time = time.time() - self.runner_time

        print("Time cost: " + str(self.runner_time / 3600) + " hours")
