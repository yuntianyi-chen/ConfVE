import random
from copy import deepcopy
from config import GENERATION_LIMIT, INIT_POP_SIZE, SELECT_NUM_RATIO


class IndividualWithFitness:

    def __init__(self, value_list):
        self.value_list = value_list
        self.reset_default()
        # self.range_list = range_list
        self.violation_intro = 0
        self.violation_remov = 0

    def update_accumulated_objectives(self, violation_results, code_coverage, execution_time):
        self.accumulated_objectives[0] += len(violation_results)
        self.accumulated_objectives[1] += code_coverage
        self.accumulated_objectives[2] += execution_time

    def calculate_fitness(self, fitness_mode):
        self.violation_number = self.accumulated_objectives[0]
        self.code_coverage = self.accumulated_objectives[1]
        self.execution_time = self.accumulated_objectives[2]

        if fitness_mode == "intro_remov":
            self.fitness = self.violation_intro+self.violation_remov
            print(f"       Vio Intro: {self.violation_intro}")
            print(f"       Vio Remov: {self.violation_remov}")

        else:
            self.fitness = self.violation_number * self.code_coverage * self.execution_time

    def update_violation_intro_remov(self, violation_results, scenario):
        for violation in violation_results:
            if violation not in scenario.original_violation_results:
                self.violation_intro+=1
        for violation in scenario.original_violation_results:
            if violation not in violation_results:
                self.violation_remov+=1


    def get_fitness(self):
        return self.fitness

    def reset_default(self):
        self.fitness = None
        # self.fitness = random.randint(0, 10)
        self.violation_number = 0
        self.code_coverage = 0
        self.execution_time = 0
        self.accumulated_objectives = [0, 0, 0]
        self.violation_intro = 0
        self.violation_remov = 0

def generate_individuals(option_obj_list):
    generated_value_lists = list()

    for i in range(INIT_POP_SIZE):
        generated_value_list = list()
        for option_obj in option_obj_list:
            option_type = option_obj.option_type
            option_value = option_obj.option_value
            # generated_value = generate_option_value_by_random(option_type, option_value)
            generated_value = option_value
            generated_value_list.append(generated_value)
        generated_value_lists.append(generated_value_list)
    individual_list = [IndividualWithFitness(value_list) for value_list in generated_value_lists]
    return individual_list


def ga_init(option_obj_list):
    # global init_population_size
    # init_population_size = INIT_POP_SIZE
    generation_limit = GENERATION_LIMIT
    option_type_list = [option_obj.option_type for option_obj in option_obj_list]
    init_individual_list = generate_individuals(option_obj_list)
    return init_individual_list, generation_limit, option_type_list


def select(individual_list, option_obj_list):
    # select 5 with the least fitness, 3 randomly from the remaining, 2 new generated
    select_num_ratio = SELECT_NUM_RATIO
    new_individual_list = get_unduplicated(individual_list, select_num_ratio, option_obj_list)
    return new_individual_list
    # return individual_list[0:init_population_size]


def get_unduplicated(individual_list, select_num_ratio, option_obj_list):
    individuals_with_least_fitness = individual_list[:select_num_ratio[0]]
    individuals_from_remaining = random.choices(individual_list[select_num_ratio[0]:], k=select_num_ratio[1])
    individuals_new_generated = generate_individuals(option_obj_list, select_num_ratio[2])
    selected_individuals_list = individuals_with_least_fitness + individuals_from_remaining + individuals_new_generated
    return selected_individuals_list


def crossover(individual_list):
    new_individual_list = list()
    individual_list_size = len(individual_list)
    for i in range(individual_list_size):
        randa = random.randint(0, individual_list_size - 1)
        randb = random.randint(0, individual_list_size - 1)
        while randb == randa:
            randb = random.randint(0, individual_list_size - 1)
        individual_A = deepcopy(individual_list[randa])
        individual_B = deepcopy(individual_list[randb])
        position = random.randint(1, len(individual_list[0].value_list) - 1)
        individual_A.value_list = individual_list[randa].value_list[:position] + individual_list[randb].value_list[
                                                                                 position:]
        individual_B.value_list = individual_list[randb].value_list[:position] + individual_list[randa].value_list[
                                                                                 position:]
        # individual_A.fitness = None
        # individual_B.fitness = None
        individual_A.reset_default()
        individual_B.reset_default()

        new_individual_list.append(individual_A)
        new_individual_list.append(individual_B)
    return individual_list + new_individual_list


def mutate(individual_list, option_type_list):
    new_individual_list = deepcopy(individual_list)
    for individual_obj in new_individual_list:
        position = random.randint(0, len(individual_list[0].value_list) - 1)
        option_type = option_type_list[position]
        option_value = individual_obj.value_list[position]
        generated_value = generate_option_value_by_random(option_type, option_value)
        individual_obj.value_list[position] = generated_value
        individual_obj.reset_default()
    return individual_list + new_individual_list


# def calculate_fitness(violation_number, code_coverage, execution_time):
#     fitness = random.uniform(0, 100)
#     return fitness



def generate_option_value_by_random(option_type, option_value):
    if option_type == "float":
        generated_value = round(random.uniform(0, 100), 2)
    elif option_type == "integer":
        generated_value = random.randint(1, 10)
    elif option_type == "string":
        generated_value = option_value
    elif option_type == "boolean":
        generated_value = random.choice(["true", "false"])
    elif option_type == "e_number":
        generated_value = option_value
    else:
        generated_value = None

    return str(generated_value)
