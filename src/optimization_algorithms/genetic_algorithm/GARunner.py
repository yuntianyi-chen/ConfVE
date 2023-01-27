import time
from config import GENERATION_LIMIT, INIT_POP_SIZE, TIME_HOUR_THRESHOLD
from optimization_algorithms.TestRunner import TestRunner
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

        for generation_num in range(GENERATION_LIMIT):
            print("-------------------------------------------------")
            print(f"Generation_{generation_num}")
            print("-------------------------------------------------")
            self.individual_num = 0
            individual_list_after_crossover = crossover(individual_list)
            individual_list_after_mutate = mutation(individual_list_after_crossover, self.config_file_obj,
                                                    self.range_analyzer)

            for generated_individual in individual_list_after_mutate:
                generated_individual.reset_default()
                ind_id = f"Generation_{str(generation_num)}_Config_{self.individual_num}"

                self.individual_running(generated_individual, ind_id)

                if time.time() - self.runner_time >= TIME_HOUR_THRESHOLD * 3600:
                    return

            individual_list = select(individual_list_after_mutate, self.config_file_obj)

            # output range analysis every generation
            self.file_output_manager.update_range_analysis_file(self.config_file_obj, self.range_analyzer,
                                                                generation_num)
            self.record_replace_and_check()

