import networkx as nx

from config import MAGGIE_ROOT, OBS_DIR
from environment.cyber_env_operation import connect_bridge, cyber_env_init
from scenario_handling.create_scenarios import Scenario
from scenario_handling.obstacle_generator import obs_generating
from scenario_handling.run_scenario import run_scenarios, register_obstacles, send_routing_request, \
    register_traffic_lights, stop_obstacles
from scenario_handling.scenario_tools import map_tools
from scenario_handling.scenario_tools.feature_generator import runOracles
from scenario_handling.scenario_tools.map_info_parser import validatePath, initialize, longerTrace, generateObsDescFile, \
    produceTrace
import random
import subprocess
import os
import time
import json
from deap import base
from deap import creator
from deap import tools

from testing_approaches.scenorita.run_oracles import run_oracles
from testing_approaches.scenorita.scenoRITA_ga import scenoRITA_ga_init

obs_folder = OBS_DIR
dest = MAGGIE_ROOT + "/data/analysis"
features_file = "mut_features.csv"
ga_file = "ga_output.csv"
timer_file = "execution_time.csv"


ptl_dict, ltp_dict, diGraph = initialize()
obstacle_type = ["PEDESTRIAN", "BICYCLE", "VEHICLE"]

class ScenoRITA:
    def __init__(self):
        return
        # self.range_list = range_list

    def obs_routing_generate(self):
        return

    def adc_routing_generate(self):
        # this function costs calculating resources
        ptl_dict, ltp_dict, diGraph = initialize()

        valid_path = False
        while not valid_path:
            p_index1 = random.randint(0, len(ptl_dict.keys()) - 1)
            p_index2 = random.randint(0, len(ptl_dict.keys()) - 1)
            start_point = tuple(map(float, list(ptl_dict.keys())[p_index1].split('-')))
            if not map_tools.all_points_not_in_junctions(start_point):
                p1 = list(ptl_dict.keys())[p_index1]
                p2 = list(ptl_dict.keys())[p_index2]
                continue
            valid_path = validatePath(p_index1, p_index2, ptl_dict, ltp_dict, diGraph)
        p1 = list(ptl_dict.keys())[p_index1]
        p2 = list(ptl_dict.keys())[p_index2]
        adc_routing = p1.replace('-', ',') + "," + p2.replace('-', ',')
        return adc_routing

def check_trajectory(p_index1, p_index2):
    valid_path = False
    while not valid_path:
        valid_path = validatePath(p_index1, p_index2, ptl_dict, ltp_dict, diGraph) and longerTrace(
            list(ptl_dict.keys())[p_index1], list(ptl_dict.keys())[p_index2], ptl_dict, ltp_dict, diGraph)
        if not valid_path:
            p_index1 = random.randint(0, len(ptl_dict.keys()) - 1)
            p_index2 = random.randint(0, len(ptl_dict.keys()) - 1)
    return p_index1, p_index2


def check_obs_type(length, width, height, speed, type_index):
    obs_type = obstacle_type[type_index]
    if obs_type == "VEHICLE":
        if length < 4.0 or length > 14.5:
            length = random.uniform(4.0, 14.5)
        if height < 1.5 or height > 4.7:
            height = random.uniform(1.5, 4.7)
        if width < 1.5 or width > 2.5:
            width = random.uniform(1.5, 2.5)
        if speed < 2.5 or speed > 20:
            speed = random.uniform(2.5, 20)
        diversity_counter["V"] += 1
    if obs_type == "PEDESTRIAN":
        if length < 0.2 or length > 0.5:
            length = random.uniform(0.2, 0.5)
        if height < 0.97 or height > 1.87:
            height = random.uniform(0.97, 1.87)
        if width < 0.3 or width > 0.8:
            width = random.uniform(0.3, 0.8)
        if speed < 1.25 or speed > 3:
            speed = random.uniform(1.25, 3)
        diversity_counter["P"] += 1
    if obs_type == "BICYCLE":
        if length < 1 or length > 2.5:
            length = random.uniform(1, 2.5)
        if height < 1 or height > 2.5:
            height = random.uniform(1, 2.5)
        if width < 0.5 or width > 1:
            width = random.uniform(0.5, 1)
        if speed < 1.75 or speed > 7:
            speed = random.uniform(1.75, 7)
        diversity_counter["B"] += 1
    return length, width, height, speed


def run_scenario(scenario, bridge):
    sim_time=time.time()
    adc_route_raw = scenario.adc_route.split(',')
    init_x, init_y, dest_x, dest_y = float(adc_route_raw[0]), float(adc_route_raw[1]), float(
        adc_route_raw[2]), float(adc_route_raw[3])

    print("    Start recorder...")
    recorder_subprocess = scenario.start_recorder()

    p = register_obstacles(scenario.obs_group_path)

    send_routing_request(init_x, init_y, dest_x, dest_y, bridge)

    ####################
    register_traffic_lights(scenario.traffic_light_control, bridge)

    # Wait for record time
    # time.sleep(MAX_RECORD_TIME)
    ####################

    # Stop recording messages and producing perception messages
    print("    Stop recorder...")
    scenario.stop_recorder(recorder_subprocess)

    # scenario.stop_subprocess(p)
    stop_obstacles(p)
    sim_time=time.time()-sim_time

    orcle_time=time.time()
    min_dist, all_lanes, min_speed, boundary_dist, accl, hardbreak, collision = run_oracles()
    orcle_time=time.time()-orcle_time

    lanes_only = ""
    for lane in all_lanes:
        lanes_only = lanes_only + lane[0] + " "
    lanes_only.strip(" ")

    if min_dist == set() or len(lanes_only) == 0:
        print(None)
    else:
        print(min_dist, lanes_only, min_speed, boundary_dist,
              accl, hardbreak, all_lanes, collision, sim_time, orcle_time,sep="\n")

    output_result = (min_dist, lanes_only, min_speed, boundary_dist, accl, hardbreak, all_lanes, collision, sim_time, orcle_time)
    # violation_number, code_coverage, execution_time = measure_objectives_individually(scenario)
    # scenario.calculate_fitness(violation_number, code_coverage, execution_time)

    # fitness = calculate_fitness(violation_number, code_coverage, execution_time)
    # generated_individual.update_accumulated_objectives(violation_number, code_coverage, execution_time)

    # if violation_number == 0:
    #     scenario.delete_record()
    return output_result

def runScenario(deme, record_name, bridge):
    # to start with a fresh set of obstacles for the current scnerio

    os.system("rm -f "+OBS_DIR+"*")
    global diversity_counter
    diversity_counter = {"V": 0, "P": 0, "B": 0}
    for ind in deme:
        p_index1, p_index2 = check_trajectory(ind[1], ind[2])
        ind[1] = p_index1
        ind[2] = p_index2
        # get the x,y coor coorespoding to index i1 and i2
        p1 = list(ptl_dict.keys())[p_index1]
        p2 = list(ptl_dict.keys())[p_index2]
        # get the correspodning lane id where the points reside
        lane1 = ptl_dict[p1]
        lane2 = ptl_dict[p2]
        # find the path between two lanes
        path = nx.shortest_path(diGraph, source=lane1, target=lane2)
        # verify that obstacle type and size is realistic
        ind[4], ind[5], ind[6], ind[7] = check_obs_type(ind[4], ind[5], ind[6], ind[7], ind[8])
        # ensure there are no two obstacles with similar id
        unique_obs_id = False
        while not unique_obs_id:
            if os.path.exists(os.path.join(obs_folder, "sunnyvale_loop_obs{}.json".format(ind[0]))):
                ind[0] = random.randint(0, 30000)
            else:
                unique_obs_id = True
        # generate the desc files (each desc file corresponds to one individual/obstacle)
        desc = generateObsDescFile(ind[0], ind[3], ind[4], ind[5], ind[6], ind[7], obstacle_type[ind[8]])
        desc = produceTrace(p1, p2, path, ltp_dict, desc)
        filename = "sunnyvale_loop_obs" + str(desc["id"]) + ".json"
        with open(os.path.join(obs_folder, filename), 'w') as outfile:
            json.dump(desc, outfile)

    approach_generator = ScenoRITA()
    scenario = Scenario(False, obs_folder, approach_generator.adc_routing_generate(), record_name)
    output_result = run_scenario(scenario, bridge)

    # scenario run successfully
    sim_time = float(output_result[8]) * num_runs
    orcle_time = float(output_result[9]) * num_runs
    lanes, min_distance, speeding_min, uslc_min, fastAccl_min, hardBrake_min = runOracles(output_result,
                                                                                          record_name, deme)
    return lanes, min_distance, speeding_min, uslc_min, fastAccl_min, hardBrake_min, sim_time, orcle_time, num_runs




if __name__ == "__main__":
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

    # store features output and evolution output
    labels = "record_name,c_x,c_y,c_type,adc_heading,adc_speed,obs_id,obs_heading,obs_speed,obs_type,obs_len,obs_wid,obs_height," \
             "speeding_x,speeding_y,speeding_value,speeding_duration,speeding_heading,lanes_speed_limit,uslc_x,uslc_y,uslc_duration,uslc_heading," \
             "fastAccl_x,fastAccl_y,fastAccl_value,fastAccl_duration,fastAccl_heading,hardBrake_x,hardBrake_y,hardBrake_value,hardBrake_duration,hardBrake_heading," \
             "c_counter,speeding_counter,uslc_counter,fastAccl_counter,hardBrake_counter,totalV\n"
    with open(os.path.join(dest, features_file), 'w') as ffile:
        ffile.write(labels)
    labels = "RecordName,ObsNum,P,B,V,AVG_OBS2ADC_Distance,Speed_Below_Limit,ADC2LaneBound_Distance,FastAccl,HardBrake\n"
    with open(os.path.join(dest, ga_file), 'a+') as gfile:
        gfile.write(labels)
    labels = "RecordName,Simulation,Oracles,MISC,E2E,RetryNo\n"
    with open(os.path.join(dest, timer_file), 'a+') as tfile:
        tfile.write(labels)

    # os.system("rm -rf /apollo/automation/grading_metrics/Safety_Violations/*")

    print("Start of evolution")
    start_time = time.time()

    bridge = connect_bridge()
    cyber_env_init()

    for deme in pop:
        e2e_time = time.time()
        record_name = "Generation{}_Scenario{}".format(g, scenario_counter)
        lanes, min_distance, speeding_min, uslc_min, fastAccl_min, hardBrake_min, sim_time, orcle_time, num_runs = runScenario(deme, record_name, bridge)
        lanes.remove('')
        GLOBAL_LANE_COVERAGE.update(lanes)
        lane_coverage[scenario_counter] = lane_coverage[scenario_counter].union(lanes)
        sum = 0
        for ind in deme:
            obs_min_dist = min_distance[str(ind[0])]
            ind.fitness.values = (obs_min_dist, speeding_min, uslc_min, fastAccl_min, hardBrake_min,)
            sum += obs_min_dist
        # with open(os.path.join(dest, ga_file), 'a+') as gfile:
        #     gfile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"
        #                 % (
        #                     record_name, len(deme), diversity_counter["P"], diversity_counter["B"], diversity_counter["V"],
        #                     sum / len(deme), speeding_min, uslc_min, fastAccl_min, hardBrake_min))
        e2e_time = time.time() - e2e_time
        misc_time = e2e_time - sim_time - orcle_time
        with open(os.path.join(dest, timer_file), 'a+') as tfile:
            tfile.write(
                "{},{:.2f},{:.2f},{:.2f},{:.2f},{}\n".format(record_name, sim_time, orcle_time, misc_time, e2e_time, num_runs))
        scenario_counter += 1

    while len(GLOBAL_LANE_COVERAGE) < TOTAL_LANES and (time.time() - start_time) <= ETIME:
        g = g + 1
        scenario_counter = 1
        print("-- Generation %i --" % g)

        bridge = connect_bridge()
        cyber_env_init()

        for deme in pop:
            e2e_time = time.time()
            offspring = list(map(toolbox.clone, deme))
            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < CXPB:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            for mutant in offspring:
                if random.random() < MUTPB:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
                if random.random() < DELPB and len(offspring) != 1:
                    worst_ind = tools.selWorst(offspring, 1)[0]
                    offspring.remove(worst_ind)
                    del mutant.fitness.values
                if random.random() < ADDPB and len(hof) != 0:
                    best_ind = hof[random.randint(0, int(len(hof) / 2))]
                    offspring.append(best_ind)
                    del mutant.fitness.values


            record_name = "Generation{}_Scenario{}".format(g, scenario_counter)

            lanes, min_distance, speeding_min, uslc_min, fastAccl_min, hardBrake_min, sim_time, orcle_time, num_runs = runScenario(offspring, record_name, bridge)
            lanes.remove('')
            GLOBAL_LANE_COVERAGE.update(lanes)
            lane_coverage[scenario_counter] = lane_coverage[scenario_counter].union(lanes)
            sum = 0
            for ind in offspring:
                obs_min_dist = min_distance[str(ind[0])]
                ind.fitness.values = (obs_min_dist, speeding_min, uslc_min, fastAccl_min, hardBrake_min,)
                sum += obs_min_dist
            # with open(os.path.join(dest, ga_file), 'a+') as gfile:
            #     gfile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"
            #                 % (record_name, len(deme), diversity_counter["P"], diversity_counter["B"],
            #                    diversity_counter["V"], sum / len(deme), speeding_min, uslc_min, fastAccl_min,
            #                    hardBrake_min))
            hof.insert(tools.selBest(offspring, 1)[0])
            deme = toolbox.select(deme + offspring, len(offspring))

            e2e_time = time.time() - e2e_time
            misc_time = e2e_time - sim_time - orcle_time
            with open(os.path.join(dest, timer_file), 'a+') as tfile:
                tfile.write(
                    "{},{:.2f},{:.2f},{:.2f},{:.2f},{}\n".format(record_name, sim_time, orcle_time, misc_time, e2e_time,
                                                                 num_runs))
            scenario_counter += 1

            if (time.time() - start_time) >= ETIME:
                break

    print("-- End of (successful) evolution --")

    # ------- Final Results -------
    end_time = time.time()
    print("-- Execution Time: %.2f  seconds --\n" % (end_time - start_time))
    print("*** Total Num. of Lanes Covered:%s out of %s ***\n" % (len(GLOBAL_LANE_COVERAGE), TOTAL_LANES))