import os
import pickle
import time

from config import APOLLO_ROOT, MAP_NAME
from scenario_handling.obstacle_generator import generate_obstacles
from tools.config_file_handler.translator_apollo import option_obj_translator, save2file


def config_file_generating(generated_individual, option_obj_list):
    generated_value_list = generated_individual.value_list
    for generated_value, option_obj in zip(generated_value_list, option_obj_list):
        option_obj.option_value = generated_value
    output_string_list = option_obj_translator(option_obj_list)
    save2file(output_string_list)


def read_obstacles():
    obs_folder = f"{APOLLO_ROOT}/modules/tools/perception/obstacles/{MAP_NAME}/"
    pop_pickle_dump_data_path = f"{APOLLO_ROOT}/modules/tools/perception/pop_pickle/{MAP_NAME}_dump_data"
    pop_pickle_dump_data_file = open(pop_pickle_dump_data_path, "rb")
    pop = pickle.load(pop_pickle_dump_data_file)
    scenario_counter = 0
    obs_group_folders_name_list = os.listdir(obs_folder)
    for obs_group_folder_name in obs_group_folders_name_list:
        # obs_files_name_list = os.listdir(obs_folder + obs_group_folder_name)

        start_time = time.time()
        # record_name="Generation{}_Scenario{}".format(generation,scenario_counter)
        record_name = "scenario_" + str(scenario_counter)

        e2e_time_start = time.time()
        runScenario(record_name, obs_group_number=scenario_counter)
        e2e_time = time.time() - e2e_time_start
        scenario_counter += 1


def runScenario(record_name, obs_group_number):
    # ------- running the scneario -------
    # bazel-bin/apollo_v7_testing/scenario_player/run_automation -rv 586115.2216681268,4140677.470931069,586131.4210111903,4140791.3412697404 -o scenario_0 -mn sunnyvale_loop -ogn 0
    # scenario_player_cmd='bazel run //apollo_v7_testing/scenario_player:run_automation -- -rv 586855.34,4140800.88,587283.52,4140882.30'+' -o '+record_name+' -mn '+map_name+' -ogn '+str(obs_group_number)
    scenario_player_cmd = 'bazel run //apollo_v7_testing/scenario_player:run_automation -- -rv 586980.86,4140959.45,587283.52,4140882.30' + ' -o ' + record_name + ' -mn ' + MAP_NAME + ' -ogn ' + str(
        obs_group_number)
    # scenario_player_cmd='bazel run //apollo_v7_testing/scenario_player:run_automation -- -rv 586855.34,4140800.88,586980.86,4140959.45'+' -o '+record_name+' -mn '+map_name+' -ogn '+str(obs_group_number)

    # adc_routing = adc_routing_generating()
    # scenario_player_cmd = 'bazel run //apollo_v7_testing/scenario_player:run_automation -- -rv ' + adc_routing + ' -o ' + record_name + ' -mn ' + map_name + ' -ogn ' + str(obs_group_number)

    # cmd = f"docker exec -d {get_container_name()} "+ scenario_player_cmd
    # subprocess.run(cmd.split())

    scenario_player_output = subprocess.check_output(scenario_player_cmd, shell=True)


def adc_routing_generating():
    return


# scenario refers to different config settings with fixed obstacles and adc routing
def create_scenarios(generated_individual, option_obj_list):
    config_file_generating(generated_individual, option_obj_list)
    read_obstacles()
    adc_routing_generating()
    return
