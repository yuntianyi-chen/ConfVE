from objectives.measure_objectives import sortNondominated, CrowdingDist

fitness = [(1, 2), (2, 2), (3, 1), (1, 4), (1, 1)]
fronts = sortNondominated(fitness)

print(fronts)


distances = CrowdingDist(fitness)


print(distances)
