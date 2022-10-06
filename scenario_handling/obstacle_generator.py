from deap import base, creator, tools
from config import OBS_DIR, APOLLO_ROOT, MAP_NAME
from scenario_handling.scenario_tools.map_info_parser import *
from scenario_handling.scenario_tools.feature_generator import *
import pickle


ptl_dict, ltp_dict, diGraph = initialize()
obstacle_type = ["PEDESTRIAN", "BICYCLE", "VEHICLE"]


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


def genetic_obs_individual_init():
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


def obs_files_generator(obs_deme, scenario_counter):
    scenario_obs_folder_path = OBS_DIR + "obs_group_" + str(scenario_counter) + "/"
    if os.path.exists(scenario_obs_folder_path):
        os.system("rm -f " + scenario_obs_folder_path + "*")
    else:
        os.makedirs(scenario_obs_folder_path)

    global diversity_counter
    diversity_counter = {"V": 0, "P": 0, "B": 0}

    obs_counter = 0
    for obs_indi in obs_deme:
        p_index1, p_index2 = check_trajectory(obs_indi[1], obs_indi[2])
        obs_indi[1] = p_index1
        obs_indi[2] = p_index2
        # get the x,y coor coorespoding to index i1 and i2
        p1 = list(ptl_dict.keys())[p_index1]
        p2 = list(ptl_dict.keys())[p_index2]
        # get the correspodning lane id where the points reside
        lane1 = ptl_dict[p1]
        lane2 = ptl_dict[p2]
        # find the path between two lanes
        path = nx.shortest_path(diGraph, source=lane1, target=lane2)
        # verify that obstacle type and size is realistic
        obs_indi[4], obs_indi[5], obs_indi[6], obs_indi[7] = check_obs_type(obs_indi[4], obs_indi[5], obs_indi[6],
                                                                            obs_indi[7], obs_indi[8])
        desc = generateObsDescFile(obs_indi[0], obs_indi[3], obs_indi[4], obs_indi[5], obs_indi[6], obs_indi[7],
                                   obstacle_type[obs_indi[8]])
        desc = produceTrace(p1, p2, path, ltp_dict, desc)
        filename = "obs_" + str(obs_counter) + ".json"
        with open(os.path.join(scenario_obs_folder_path, filename), 'w') as outfile:
            json.dump(desc, outfile)
        obs_counter += 1


def obs_settings():
    global NP
    NP = 10
    OBS_MAX = 20
    OBS_MIN = 10
    # TOTAL_LANES=60
    # ETIME=43200 # execution time end (in seconds) after 12 hours 
    DEME_SIZES = [random.randint(OBS_MIN, OBS_MAX) for p in range(0, NP)]
    # CXPB, MUTPB, ADDPB, DELPB = 0.8, 0.2, 0.1, 0.1

    return DEME_SIZES


def obs_generating(toolbox):
    DEME_SIZES = obs_settings()
    pop = [toolbox.deme(n=i) for i in DEME_SIZES]
    pop_pickle_dump_data_path = f"{APOLLO_ROOT}/modules/tools/perception/pop_pickle/{MAP_NAME}_dump_data"

    with open(pop_pickle_dump_data_path, 'wb') as f:
        pickle.dump(pop, f, protocol=4)

    scenario_counter = 0
    for obs_deme in pop:
        obs_files_generator(obs_deme, scenario_counter)
        scenario_counter += 1


def generate_obstacles():
    toolbox = genetic_obs_individual_init()
    obs_generating(toolbox)


if __name__ == "__main__":
    generate_obstacles()
