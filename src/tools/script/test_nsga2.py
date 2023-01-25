import random

from config import INIT_POP_SIZE
from optimization_algorithms.genetic_algorithm.nsga2 import sort_nondominated, crowding_dist


def get_rand():
    return random.uniform(1, 100)


class AA:
    def __init__(self, a, b, c):
        self.fitness = (a, b, c)


individual_list = [AA(get_rand(), get_rand(), get_rand()) for i in range(20)]

fitness_list = [individual.fitness for individual in individual_list]
fronts = sort_nondominated(fitness_list)
distances = crowding_dist(fitness_list)

select_counter = 0
selected_index_list = []
for sub_fronts_list in fronts:
    if select_counter + len(sub_fronts_list) < INIT_POP_SIZE:
        selected_index_list += sub_fronts_list
        select_counter += len(sub_fronts_list)
    else:
        sub_indexed_distances = [(index, distances[index]) for index in sub_fronts_list]
        sub_indexed_distances.sort(reverse=True, key=lambda x: x[1])
        sub_select_num = INIT_POP_SIZE - select_counter
        for index, distance in sub_indexed_distances[:sub_select_num]:
            selected_index_list.append(index)
        break

new_individual_list = [individual_list[index] for index in selected_index_list]

print(distances)
