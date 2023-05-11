import time
from config import GENERATION_LIMIT, TIME_HOUR_THRESHOLD, POP_SIZE, OFFSPRING_SIZE
from optimization_algorithms.TestRunner import TestRunner
from optimization_algorithms.genetic_algorithm.ga import select, generate_individuals, init_mutation, ga_operation


class GARunner(TestRunner):
    def __init__(self, containers):
        super().__init__(containers)
        self.ga_runner()

    def ga_runner(self):
        # print("Start GA")
        init_individual_list = generate_individuals(self.config_file_obj, POP_SIZE + OFFSPRING_SIZE)

        # initial mutation
        init_individual_list = init_mutation(init_individual_list, self.config_file_obj, self.range_analyzer)
        self.individual_num = 0
        for init_individual in init_individual_list:
            ind_id = f"Init_Config_{self.individual_num}"
            self.individual_running(init_individual, ind_id)

        individual_list = select(init_individual_list, self.config_file_obj)

        # individual_list=init_individual_list
        for generation_num in range(GENERATION_LIMIT):
            print("-------------------------------------------------")
            print(f"Generation_{generation_num}")
            print("-------------------------------------------------")
            self.individual_num = 0
            # offspring_list_of_crossover = crossover(individual_list)
            # offspring_list_of_mutation = mutation(individual_list, self.config_file_obj,
            #                                         self.range_analyzer)
            offspring_list = ga_operation(individual_list, self.config_file_obj, self.range_analyzer)
            for generated_individual in offspring_list:
                if not generated_individual.fitness:
                    # generated_individual.reset_default()
                    ind_id = f"Generation_{str(generation_num)}_Config_{self.individual_num}"

                    self.individual_running(generated_individual, ind_id)

                    if time.time() - self.runner_time >= TIME_HOUR_THRESHOLD * 3600:
                        return

            individual_list = select(individual_list+offspring_list, self.config_file_obj)

            # output range analysis every generation
            self.file_output_manager.update_range_analysis_file(self.config_file_obj, self.range_analyzer,
                                                                generation_num)
            self.record_replace_and_check()

