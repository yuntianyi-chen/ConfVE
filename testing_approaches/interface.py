import os
from config import APOLLO_ROOT, MAP_NAME, AV_TESTING_APPROACH, OBS_GROUP_COUNT
from testing_approaches.obstacle_obj import ObsWithFitness
from testing_approaches.scenorita.scenorita import ScenoRITA



def init_obs():
    obstacle_chromosomes_list = [ObsWithFitness() for i in range(OBS_GROUP_COUNT)]
    return obstacle_chromosomes_list


def generate_obs_adc_routes_by_approach(obstacle_chromosomes):
    approach_generator = None
    if AV_TESTING_APPROACH == "scenoRITA":
        approach_generator = ScenoRITA()
    obs_group_path_list = [approach_generator.obs_routing_generate() for i in range(OBS_GROUP_COUNT)]
    obs_group_path_list = read_obstacles()
    adc_routing_list = [approach_generator.adc_routing_generate() for i in range(OBS_GROUP_COUNT)]

    # adc_routing = adc_routing_generate()
    # adc_routing_list = ["586980.86,4140959.45,587283.52,4140882.30" for i in obs_group_path_list]

    return obs_group_path_list, adc_routing_list


def read_obstacles():
    obs_folder = f"{APOLLO_ROOT}/modules/tools/perception/obstacles/{MAP_NAME}/"
    obs_apollo_folder = f"{MAP_NAME}/"
    obs_group_folders_name_list = os.listdir(obs_folder)
    obs_group_folders_name_list.sort()
    obs_group_path_list = []
    for obs_group_folder_name in obs_group_folders_name_list:
        obs_group_path_list.append(obs_apollo_folder + obs_group_folder_name)
    return obs_group_path_list


