import time
from config import T_STRENGTH_VALUE, TIME_HOUR_THRESHOLD, POP_SIZE
from optimization_algorithms.TestRunner import TestRunner
from optimization_algorithms.baseline.TwiseTuner import TwiseTuner
from optimization_algorithms.genetic_algorithm.ga import generate_individuals


class OneEnabledRunner(TestRunner):
    def __init__(self, containers):
        super().__init__(containers)
        self.twise_tuner = TwiseTuner(self.config_file_obj, self.range_analyzer, T=1)
        self._runner()

    def _runner(self):
        while True:
            tested_ind_count = 0
            option_id = 0

            while tested_ind_count < 20:
                default_individual = generate_individuals(self.config_file_obj, population_size=1)[0]
                generated_individual_list = self.twise_tuner.tune_individual(default_individual, self.range_analyzer)

                id_count = 0
                for generated_individual in generated_individual_list:
                    self.individual_running(generated_individual, f"Config_{option_id}_{id_count}")

                    tested_ind_count += 1
                    id_count += 1
                    if time.time() - self.runner_time >= TIME_HOUR_THRESHOLD * 3600:
                        return
                option_id += 1
            self.file_output_manager.update_range_analysis_file(self.config_file_obj, self.range_analyzer,
                                                                self.individual_num)
            self.record_replace_and_check()
