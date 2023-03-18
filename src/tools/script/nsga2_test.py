from optimization_algorithms.genetic_algorithm.nsga2 import sort_nondominated, crowding_dist

fitness_list = [(1,2,4), (3,1,5), (5,0,8)]

fronts_index_list = sort_nondominated(fitness_list)
distances_list = crowding_dist(fitness_list)

print()