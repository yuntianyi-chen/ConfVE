import time
from config import TIME_HOUR_THRESHOLD
from optimization_algorithms.TestRunner import TestRunner
from optimization_algorithms.genetic_algorithm.ga import generate_individuals


class PreAnalyzeRunner(TestRunner):
    def __init__(self, containers):
        super().__init__(containers)
        # self.tested_stage_list = [-5000, -2500, -1000, -500, -250, 250, 500, 1000, 2500, 5000]
        self.tested_fixed_value_list = [-5001, -1001, -101, -1, 0, 1, 101, 1001, 5001]
        self._runner()

    def _runner(self):
        position_list = list(range(self.config_file_obj.option_count))

        option_id=0
        for position in position_list:
            option_type = self.config_file_obj.option_type_list[position]

            generated_individual_list = []
            if option_type in ["float", "integer"]:
                default_individuals = generate_individuals(self.config_file_obj,
                                                           population_size=len(self.tested_fixed_value_list))
                # for tested_stage, individual in zip(self.tested_stage_list, default_individuals):
                for tested_value, individual in zip(self.tested_fixed_value_list, default_individuals):
                    # option_value = individual.value_list[position]
                    # generated_value = str(eval(option_value) + tested_stage)
                    generated_value = str(tested_value)
                    self.range_analyzer.tune_one_value_with_generated(individual, self.config_file_obj,
                                                                      position, option_type, generated_value)
                    generated_individual_list.append(individual)
                id_count = 0
                for generated_individual in generated_individual_list:
                    self.individual_running(generated_individual, f"Config_{option_id}_{id_count}")
                    id_count += 1
                    self.file_output_manager.update_range_analysis_file(self.config_file_obj, self.range_analyzer,
                                                                  self.individual_num)
                option_id += 1
        self.file_output_manager.dump_range_analyzer(self.range_analyzer)
