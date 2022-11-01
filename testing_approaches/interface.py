import os
from config import APOLLO_ROOT, MAP_NAME, AV_TESTING_APPROACH, OBS_GROUP_COUNT
from testing_approaches.scenorita.scenorita import adc_routing_generate, obs_routing_generate


def generate_obs_adc_routes_by_approach(obstacle_chromosomes):

    # obs_group_path_list = obs_routing_generator(AV_TESTING_APPROACH)

    obs_group_path_list = read_obstacles()

    adc_routing_list = adc_routing_generator(AV_TESTING_APPROACH)
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


def adc_routing_generator(AV_TESTING_APPROACH):
    adc_routing_list = []
    if AV_TESTING_APPROACH == "scenoRITA":
        adc_routing_list = [adc_routing_generate() for i in range(OBS_GROUP_COUNT)]
    return adc_routing_list


def obs_routing_generator(AV_TESTING_APPROACH):
    obs_group_path_list = []
    if AV_TESTING_APPROACH == "scenoRITA":
        obs_group_path_list = [obs_routing_generate() for i in range(OBS_GROUP_COUNT)]
    return obs_group_path_list
