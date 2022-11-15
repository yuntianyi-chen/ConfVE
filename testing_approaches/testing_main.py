import random
import time
from config import APOLLO_ROOT, MODULE_NAME
from environment.cyber_env_operation import cyber_env_init, delete_records, connect_bridge
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.run_scenario import run_scenarios
from testing_approaches.interface import generate_obs_adc_routes_by_approach, init_obs
from testing_approaches.scenorita.scenoRITA_ga import scenoRITA_ga_init, crossover, mutate, select
from deap import tools


def ga_main(module_config_path):
    toolbox = scenoRITA_ga_init()

    NP = 50
    OBS_MAX = 15
    OBS_MIN = 3
    TOTAL_LANES = 60
    ETIME = 43200  # execution time end (in seconds) after 12 hours
    GLOBAL_LANE_COVERAGE = set()
    DEME_SIZES = [random.randint(OBS_MIN, OBS_MAX) for p in range(0, NP)]
    CXPB, MUTPB, ADDPB, DELPB = 0.8, 0.2, 0.1, 0.1

    pop = [toolbox.deme(n=i) for i in DEME_SIZES]
    hof = tools.HallOfFame(NP)  # best ind in each scenario
    lane_coverage = {scenario_num: set() for scenario_num in range(1, NP + 1)}
    scenario_counter = 1
    g = 0

    # individual_list = init_individual_list

    delete_records()

    start_time = time.time()

    # obstacle_chromosomes_list = init_obs()

    for generation_num in range(generation_limit):
        print("-------------------------------------------------")
        print(f"Generation_{generation_num}")
        print("-------------------------------------------------")
        # cyber_env_init()
        bridge = connect_bridge()
        individual_list_after_crossover = crossover(individual_list)
        individual_list_after_mutate = mutate(individual_list_after_crossover, option_type_list)
        individual_num = 0

        ###################

        obs_group_path_list, adc_routing_list = generate_obs_adc_routes_by_approach(obstacle_chromosomes_list)
        ###################

        for generated_individual in individual_list_after_mutate:
            print("-------------------------------------------------")
            print(f"Generation_{generation_num} Individual_{individual_num}")
            # Restart cyber_env to fix the image static bug here
            cyber_env_init()
            if generated_individual.fitness is None:
                # scenario refers to a config setting with different fixed obstacles and adc routes
                scenario_list = create_scenarios(generated_individual, option_obj_list, generation_num, individual_num,
                                                 obs_group_path_list, adc_routing_list)

                # test each config settings under several groups of obstacles and adc routes
                run_scenarios(generated_individual, scenario_list, bridge)

                generated_individual.calculate_fitness()

                individual_num += 1

        random.shuffle(individual_list_after_mutate)

        # Fitness the more, the better, currently, for testing
        individual_list_after_mutate.sort(reverse=True, key=lambda x: x.fitness)
        individual_list = select(individual_list_after_mutate, option_obj_list)

    end_time = time.time()
    print("Time cost: " + str((end_time - start_time) / 3600) + " hours")


if __name__ == '__main__':
    module_config_path = f"{APOLLO_ROOT}/modules/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
    ga_main(module_config_path)
