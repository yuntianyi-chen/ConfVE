import random
from copy import deepcopy
from config import SELECT_NUM_RATIO
from optimization_algorithms.genetic_algorithm.IndividualWithFitness import IndividualWithFitness
from range_analysis.OptionTuningItem import OptionTuningItem


def generate_individuals(config_file_obj, population_size):
    generated_value_lists = list()
    for i in range(population_size):
        generated_value_list = list()
        for option_value in config_file_obj.default_option_value_list:
            generated_value = option_value
            generated_value_list.append(generated_value)
        generated_value_lists.append(generated_value_list)
    individual_list = [IndividualWithFitness(value_list) for value_list in generated_value_lists]
    return individual_list


def select(individual_list, config_file_obj):
    filtered_individual_list = [item for item in individual_list if item.allow_selection]
    # select x with the least fitness, y randomly from the remaining, z new generated
    select_num_ratio = SELECT_NUM_RATIO
    new_individual_list = get_unduplicated(filtered_individual_list, select_num_ratio, config_file_obj)
    return new_individual_list


def get_unduplicated(individual_list, select_num_ratio, config_file_obj):
    individuals_with_least_fitness = individual_list[:select_num_ratio[0]]
    individuals_from_remaining = random.choices(individual_list[select_num_ratio[0]:], k=select_num_ratio[1])
    individuals_new_generated = generate_individuals(config_file_obj, select_num_ratio[2])
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

        individual_A.pre_value_list = deepcopy(individual_A.value_list)
        individual_B.pre_value_list = deepcopy(individual_B.value_list)

        position = random.randint(1, len(individual_list[0].value_list) - 1)
        individual_A.value_list = individual_list[randa].value_list[:position] + individual_list[randb].value_list[
                                                                                 position:]
        individual_B.value_list = individual_list[randb].value_list[:position] + individual_list[randa].value_list[
                                                                                 position:]

        individual_A.reset_default()
        individual_B.reset_default()

        individual_A.option_tuning_tracking_list.append("crossover")
        individual_B.option_tuning_tracking_list.append("crossover")

        new_individual_list.append(individual_A)
        new_individual_list.append(individual_B)
    return individual_list + new_individual_list


def mutate(individual_list, config_file_obj, range_analyzer):
    for individual_obj in individual_list:
        succ_tuning = False
        while (not succ_tuning):
            position = random.randint(0, len(individual_list[0].value_list) - 1)
            option_type = config_file_obj.option_type_list[position]

            if option_type in ["float", "integer", "boolean", "e_number"]:
                succ_tuning = True
                option_value = individual_obj.value_list[position]
                individual_obj.pre_value_list = deepcopy(individual_obj.value_list)

                # generated_value = generate_option_value_by_random(option_type, option_value)
                generated_value = generate_option_value_from_range(option_type, option_value,
                                                                   range_analyzer.range_list[position])

                individual_obj.value_list[position] = generated_value
                individual_obj.reset_default()

                individual_obj.option_tuning_tracking_list.append(
                    OptionTuningItem(position, option_type, config_file_obj.option_obj_list[position].option_key,
                                     individual_obj.pre_value_list[position],
                                     individual_obj.value_list[position], config_file_obj.option_obj_list[position]))

    return individual_list


def mutation(individual_list, config_file_obj, range_analyzer):
    new_individual_list = mutate(deepcopy(individual_list), config_file_obj, range_analyzer)
    return individual_list + new_individual_list


def generate_option_value_from_range(option_type, option_value, option_range):
    if option_type == "float":
        round_bit = len(option_value.split(".")[1])
        generated_value = round(random.uniform(option_range[0], option_range[1]), round_bit)
    elif option_type == "integer":
        generated_value = random.randint(option_range[0], option_range[1])
    elif option_type == "boolean":
        generated_value = "true" if option_value == "false" else "false"
    elif option_type == "string":
        generated_value = option_value
    elif option_type == "e_number":
        exp = random.randint(option_range[0], option_range[1])
        forward = option_value.split("e")[0]
        generated_value = f"{forward}e{exp}"
    else:
        generated_value = option_value

    return str(generated_value)
