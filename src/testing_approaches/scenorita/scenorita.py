# PYTHONPATH=src python3.8 src/testing_approaches/scenorita/scenorita.py

import glob
import shutil
import random
import os
import subprocess
import time
import json
from datetime import date
import networkx as nx
from config import OBS_DIR, MAX_RECORD_TIME, MAP_NAME, APOLLO_RECORDS_DIR, PROJECT_ROOT, APOLLO_ROOT, FLAGFILE_PATH, DIR_ROOT
from environment.InitRunner import InitRunner
from modules.routing.proto.routing_pb2 import RoutingRequest
from environment.Container import Container
from environment.MapLoader import MapLoader
from modules.common.proto.geometry_pb2 import PointENU
from scenario_handling.MessageGenerator import MessageGenerator
from testing_approaches.scenorita.run_oracles import run_oracles
from testing_approaches.scenorita.scenoRITA_config import OBS_MIN, OBS_MAX, NP, TOTAL_LANES, ETIME, CXPB, MUTPB, ADDPB, \
    DELPB
from deap import base, creator, tools
from scenario_handling.create_scenarios import Scenario
from testing_approaches.scenorita.random_generation import adc_routing_generate
from testing_approaches.scenorita.auxiliary.feature_generator import runOracles
from testing_approaches.scenorita.auxiliary.map_info_parser import validatePath, initialize, longerTrace, \
    generateObsDescFile, \
    produceTrace
from tools.bridge.CyberBridge import Topics
from tools.hdmap.MapParser import MapParser

obs_folder = OBS_DIR + "/scenorita/"
dest = PROJECT_ROOT + "/data/analysis"
features_file = "mut_features.csv"
ga_file = "ga_output.csv"
timer_file = "execution_time.csv"
adc_route_file = "adc_route.csv"

ptl_dict, ltp_dict, diGraph, obs_diGraph = initialize()
obstacle_type = ["PEDESTRIAN", "BICYCLE", "VEHICLE"]


def get_container_name():
    return "apollo_dev_cloudsky"


def send_routing_request(init_x, init_y, dest_x, dest_y, bridge):
    routing_request = RoutingRequest()

    # define header
    # routing_request.header.timestamp_sec = cyber_time.Time.now().to_sec()
    routing_request.header.timestamp_sec = time.time()

    routing_request.header.module_name = "routing routing..."
    routing_request.header.sequence_num = 0

    # define way points (start and end)
    start_waypoint = routing_request.waypoint.add()
    start_waypoint.pose.x = init_x
    start_waypoint.pose.y = init_y

    end_waypoint = routing_request.waypoint.add()
    end_waypoint.pose.x = dest_x
    end_waypoint.pose.y = dest_y

    bridge.publish(Topics.RoutingRequest, routing_request.SerializeToString())


def delete_recorder_log():
    files = glob.glob(f'{APOLLO_ROOT}/cyber_recorder.log.INFO.*')
    for file in files:
        os.remove(file)


def register_obstacles(obs_group_path):
    cmd = f"docker exec -d {get_container_name()} /apollo/modules/tools/perception/obstacles_perception.bash " + obs_group_path
    p = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return p


def stop_obstacles(p):
    cmd = f"docker exec -d {get_container_name()} /apollo/scripts/my_scripts/stop_obstacles.sh"
    subprocess.run(cmd.split())


def scenoRITA_ga_init():
    # global init_population_size
    # init_population_size = INIT_POP_SIZE
    # generation_limit = GENERATION_LIMIT
    # option_type_list = [option_obj.option_type for option_obj in option_obj_list]
    # init_individual_list = generate_individuals(option_obj_list)

    # ------- GA Definitions -------
    # Fitness and Individual generator
    creator.create("MultiFitness", base.Fitness, weights=(-1.0, -1.0, -1.0, 1.0, -1.0))
    creator.create("Individual", list, fitness=creator.MultiFitness)
    toolbox = base.Toolbox()
    # Attribute generator (9 obstacle attributes)
    toolbox.register("id", random.randint, 0, 30000)
    toolbox.register("start_pos", random.randint, 0, len(ptl_dict.keys()) - 1)
    toolbox.register("end_pos", random.randint, 0, len(ptl_dict.keys()) - 1)
    toolbox.register("theta", random.uniform, -3.14, 3.14)
    toolbox.register("length", random.uniform, 0.2, 14.5)
    toolbox.register("width", random.uniform, 0.3, 2.5)
    toolbox.register("height", random.uniform, 0.97, 4.7)
    toolbox.register("speed", random.uniform, 1, 20)
    toolbox.register("type", random.randint, 0, 2)
    # Structure initializers
    toolbox.register("individual", tools.initCycle, creator.Individual,
                     (toolbox.id, toolbox.start_pos, toolbox.end_pos, toolbox.theta, toolbox.length, toolbox.width,
                      toolbox.height, toolbox.speed, toolbox.type), n=1)
    # define the deme to be a list of individuals (obstacles)
    toolbox.register("deme", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=(0, 0, 0, -3, 1, 1, 1, 1, 0),
                     up=(30000, len(ptl_dict.keys()) - 1, len(ptl_dict.keys()) - 1, 3, 15, 3, 5, 20, 2), indpb=0.05)
    toolbox.register("select", tools.selNSGA2)

    return toolbox


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


def run_scenario(scenario: Scenario, ctn: Container):
    sim_time = time.time()
    adc_route_raw = scenario.adc_route.split(',')
    init_x, init_y, dest_x, dest_y = float(adc_route_raw[0]), float(adc_route_raw[1]), float(
        adc_route_raw[2]), float(adc_route_raw[3])

    scenario.heading = MapParser.get_instance().get_heading_for_coordinate(init_x, init_y)
    scenario.coord = PointENU(x=init_x, y=init_y)

    ctn.modules_operation(operation="start")
    ctn.stop_sim_control_standalone()
    ctn.start_sim_control_standalone()
    ctn.message_handler.send_initial_localization(scenario)
    # ctn.stop_sim_control_standalone_v7()
    # ctn.start_sim_control_standalone_v7(scenario.coord.x, scenario.coord.y, scenario.heading)

    print("    Start recorder...")
    ctn.start_recorder(scenario.record_name)

    p = register_obstacles(scenario.obs_group_path)

    send_routing_request(init_x, init_y, dest_x, dest_y, ctn.bridge)

    ####################
    # register_traffic_lights(scenario.traffic_light_control, bridge)

    # Wait for record time
    time.sleep(MAX_RECORD_TIME)
    ####################

    # Stop recording messages and producing perception messages
    print("    Stop recorder...")
    ctn.stop_recorder()

    # scenario.stop_subprocess(p)
    stop_obstacles(p)
    sim_time = time.time() - sim_time

    orcle_time = time.time()
    min_dist, all_lanes, min_speed, boundary_dist, accl, hardbreak, collision = run_oracles(scenario.record_name)
    orcle_time = time.time() - orcle_time

    lanes_only = ""
    for lane in all_lanes:
        lanes_only = lanes_only + lane[0] + " "
    lanes_only.strip(" ")

    if min_dist == set() or len(lanes_only) == 0:
        print(None)
    else:
        print(min_dist, lanes_only, min_speed, boundary_dist,
              accl, hardbreak, all_lanes, collision, sim_time, orcle_time, sep="\n")

    output_result = (
        min_dist, lanes_only, min_speed, boundary_dist, accl, hardbreak, all_lanes, collision, sim_time, orcle_time)
    # violation_number, code_coverage, execution_time = measure_objectives_individually(scenario)
    # scenario.calculate_fitness(violation_number, code_coverage, execution_time)

    # fitness = calculate_fitness(violation_number, code_coverage, execution_time)
    # generated_individual.update_accumulated_objectives(violation_number, code_coverage, execution_time)

    # if violation_number == 0:
    #     scenario.delete_record()
    # print(output_result)
    return output_result


def runScenario(deme, record_name, ctn: Container):
    # to start with a fresh set of obstacles for the current scnerio
    if os.path.exists(obs_folder):
        os.system("rm -f " + obs_folder + "*")
    else:
        os.makedirs(obs_folder)

    obs_apollo_folder = f"{MAP_NAME}/scenorita"

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
            if os.path.exists(os.path.join(obs_folder, "obs_{}.json".format(ind[0]))):
                ind[0] = random.randint(0, 30000)
            else:
                unique_obs_id = True
        # generate the desc files (each desc file corresponds to one individual/obstacle)
        desc = generateObsDescFile(ind[0], ind[3], ind[4], ind[5], ind[6], ind[7], obstacle_type[ind[8]])
        desc = produceTrace(p1, p2, path, ltp_dict, desc)
        filename = "obs_" + str(desc["id"]) + ".json"
        with open(os.path.join(obs_folder, filename), 'w') as outfile:
            json.dump(desc, outfile)

    failed = True
    num_runs = 0
    while failed:
        print(f"---------------------------------- trial {num_runs}")

        # if scenario has been restarted x times, restart the moodules and sim control
        if num_runs % 10 == 0 and num_runs != 0:
            ctn.cyber_env_init()
            print("attempted %s run" % num_runs)

        # approach_generator = ScenoRITA()
        adc_route = adc_routing_generate()
        scenario = Scenario(record_name, record_id=0)
        scenario.update_obs_adc(obs_apollo_folder, adc_route)
        output_result = run_scenario(scenario, ctn)
        num_runs = num_runs + 1
        # print(scenario_player_output)
        # if the adc didn't move or the adc was travelling outside the map boundaries, then re-run scenrio with new routing info
        if output_result == 'None':
            continue

        min_distance = output_result[0]
        # print(f"min_distance: {len(min_distance)}")
        # print(f"deme: {len(deme)}")
        # the return number of obstacles must match the ones in the individual
        if len(min_distance) != len(deme):
            continue
        else:
            failed = False
    # scenario run successfully
    sim_time = float(output_result[8]) * num_runs
    orcle_time = float(output_result[9]) * num_runs
    lanes, min_distance, speeding_min, uslc_min, fastAccl_min, hardBrake_min = runOracles(output_result,
                                                                                          record_name, deme, adc_route)

    return lanes, min_distance, speeding_min, uslc_min, fastAccl_min, hardBrake_min, sim_time, orcle_time, num_runs


def delete_records(records_path, mk_dir):
    if os.path.exists(records_path):
        shutil.rmtree(records_path)
    if mk_dir:
        os.makedirs(records_path)


if __name__ == "__main__":
    # delete_records()
    delete_records(records_path=APOLLO_RECORDS_DIR, mk_dir=True)
    map_instance = MapLoader().map_instance

    InitRunner()

    ctn: Container = Container(APOLLO_ROOT, f'cloudsky')

    ctn.start_instance()
    ctn.cyber_env_init()
    ctn.connect_bridge()
    ctn.create_message_handler(map_instance)
    print(f'Dreamview at http://{ctn.ip}:{ctn.port}')

    ctn.dreamview.reset()

    toolbox = scenoRITA_ga_init()

    GLOBAL_LANE_COVERAGE = set()
    DEME_SIZES = [random.randint(OBS_MIN, OBS_MAX) for p in range(0, NP)]
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
    if not os.path.exists(dest):
        os.makedirs(dest)
    with open(os.path.join(dest, features_file), 'w') as ffile:
        ffile.write(labels)
    labels = "RecordName,ObsNum,AVG_OBS2ADC_Distance,Speed_Below_Limit,ADC2LaneBound_Distance,FastAccl,HardBrake\n"
    with open(os.path.join(dest, ga_file), 'w') as gfile:
        gfile.write(labels)
    labels = "RecordName,Simulation,Oracles,MISC,E2E,RetryNo\n"
    with open(os.path.join(dest, timer_file), 'w') as tfile:
        tfile.write(labels)
    labels = "RecordName,x_start,y_start,x_end,y_end\n"
    with open(os.path.join(dest, adc_route_file), 'w') as rfile:
        rfile.write(labels)

    # os.system("rm -rf /apollo/automation/grading_metrics/Safety_Violations/*")

    print("Start of evolution")
    start_time = time.time()

    bridge = ctn.connect_bridge()
    ctn.cyber_env_init()

    for deme in pop:
        e2e_time = time.time()
        record_name = "Generation{}_Scenario{}".format(g, scenario_counter)
        lanes, min_distance, speeding_min, uslc_min, fastAccl_min, hardBrake_min, sim_time, orcle_time, num_runs = runScenario(
            deme, record_name, ctn)
        lanes.remove('')
        GLOBAL_LANE_COVERAGE.update(lanes)
        lane_coverage[scenario_counter] = lane_coverage[scenario_counter].union(lanes)
        sum = 0
        for ind in deme:
            obs_min_dist = min_distance[str(ind[0])]
            ind.fitness.values = (obs_min_dist, speeding_min, uslc_min, fastAccl_min, hardBrake_min,)
            sum += obs_min_dist
        with open(os.path.join(dest, ga_file), 'a+') as gfile:
            gfile.write("%s,%s,%s,%s,%s,%s,%s\n"
                        % (
                            record_name, len(deme), sum / len(deme), speeding_min, uslc_min, fastAccl_min,
                            hardBrake_min))
        e2e_time = time.time() - e2e_time
        misc_time = e2e_time - sim_time - orcle_time
        with open(os.path.join(dest, timer_file), 'a+') as tfile:
            tfile.write(
                "{},{:.2f},{:.2f},{:.2f},{:.2f},{}\n".format(record_name, sim_time, orcle_time, misc_time, e2e_time,
                                                             num_runs))
        scenario_counter += 1

    while (time.time() - start_time) <= ETIME:

        # while len(GLOBAL_LANE_COVERAGE) < TOTAL_LANES and (time.time() - start_time) <= ETIME:
        g = g + 1
        scenario_counter = 1
        print("-- Generation %i --" % g)

        ############
        bridge = ctn.connect_bridge()
        ctn.cyber_env_init()
        #############

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

            lanes, min_distance, speeding_min, uslc_min, fastAccl_min, hardBrake_min, sim_time, orcle_time, num_runs = runScenario(
                offspring, record_name, ctn)
            lanes.remove('')
            GLOBAL_LANE_COVERAGE.update(lanes)
            lane_coverage[scenario_counter] = lane_coverage[scenario_counter].union(lanes)
            sum = 0
            for ind in offspring:
                obs_min_dist = min_distance[str(ind[0])]
                ind.fitness.values = (obs_min_dist, speeding_min, uslc_min, fastAccl_min, hardBrake_min,)
                sum += obs_min_dist
            with open(os.path.join(dest, ga_file), 'a+') as gfile:
                gfile.write("%s,%s,%s,%s,%s,%s,%s\n"
                            % (record_name, len(deme), sum / len(deme), speeding_min, uslc_min, fastAccl_min,
                               hardBrake_min))
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

    obs_folder = OBS_DIR + "scenorita"
    temp_obs_dir = f"{DIR_ROOT}/Backup/scenoRITA/temp_obstacles"
    backup_obs_dir = f"{DIR_ROOT}/Backup/scenoRITA/obstacles/{date.today()}"
    shutil.copytree(temp_obs_dir, backup_obs_dir)
    shutil.rmtree(temp_obs_dir)
    backup_record_dir = f"{DIR_ROOT}/Backup/scenoRITA/records/{date.today()}"
    shutil.copytree(APOLLO_RECORDS_DIR, backup_record_dir)
