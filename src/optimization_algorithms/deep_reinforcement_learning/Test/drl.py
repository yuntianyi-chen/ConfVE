from config import GENERATION_LIMIT, INIT_POP_SIZE


class IndividualInDRL:

    def __init__(self, value_list):
        self.value_list = value_list
        self.reset_default()
        # self.range_list = range_list

    def update_accumulated_objectives(self, violation_number, code_coverage, execution_time):
        self.accumulated_objectives[0] += violation_number
        self.accumulated_objectives[1] += code_coverage
        self.accumulated_objectives[2] += execution_time

    def calculate_value(self):
        self.violation_number = self.accumulated_objectives[0]
        self.code_coverage = self.accumulated_objectives[1]
        self.execution_time = self.accumulated_objectives[2]
        self.value = self.violation_number * self.code_coverage * self.execution_time

    def get_value(self):
        return self.value

    def reset_default(self):
        self.value = None
        # self.fitness = random.randint(0, 10)

        self.violation_number = 0
        self.code_coverage = 0
        self.execution_time = 0
        self.accumulated_objectives = [0, 0, 0]


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
    individual_list = [IndividualInDRL(value_list) for value_list in generated_value_lists]
    return individual_list

def drl_init(option_obj_list):
    generation_limit = GENERATION_LIMIT
    option_type_list = [option_obj.option_type for option_obj in option_obj_list]
    init_individual_list = generate_individuals(option_obj_list)
    return init_individual_list, generation_limit, option_type_list


def change_individuals(individual_list, option_type_list):
    return