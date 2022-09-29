# import ptvsd
# ptvsd.enable_attach(address=('localhost', 5724), redirect_output=True)
# # print('Now is a good time to attach your debugger: Run: Python: Attach')
# ptvsd.wait_for_attach()

from cProfile import run
import subprocess
import time
from deap import base, creator, tools

from config import APOLLO_ROOT, CSV_DIR
from container_control.container_settings import get_container_name
from map_info_parser import *
from feature_generator import *
from auxiliary.map import map_tools
import pickle
from deap import base, creator, tools

from run_scenarios.toggle_sim_control import run_sim_control

# from os import listdir
# from os.path import isfile, join

map_name = "sunnyvale_loop"
# map_name="borregas_ave"
# map_name="san_mateo"

# obs_folder = "/apollo/modules/tools/perception/obstacles/" + map_name + "/"
obs_folder = f"{APOLLO_ROOT}/modules/tools/perception/obstacles/" + map_name + "/"

ptl_dict, ltp_dict, diGraph = initialize()


# obstacle_type=["PEDESTRIAN","BICYCLE","VEHICLE"]


def output_results():
    global features_file, ga_file, timer_file
    # dest = "/apollo/apollo_v7_testing/output_results/"
    dest = CSV_DIR
    features_file = dest + "mut_features.csv"
    ga_file = dest + "ga_output.csv"
    timer_file = dest + "execution_time.csv"
    # store features output and evolution output
    labels = "record_name,c_x,c_y,c_type,adc_heading,adc_speed,obs_id,obs_heading,obs_speed,obs_type,obs_len,obs_wid,obs_height," \
             "speeding_x,speeding_y,speeding_value,speeding_duration,speeding_heading,lanes_speed_limit,uslc_x,uslc_y,uslc_duration,uslc_heading," \
             "fastAccl_x,fastAccl_y,fastAccl_value,fastAccl_duration,fastAccl_heading,hardBrake_x,hardBrake_y,hardBrake_value,hardBrake_duration,hardBrake_heading," \
             "c_counter,speeding_counter,uslc_counter,fastAccl_counter,hardBrake_counter,totalV\n"
    with open(features_file, 'w') as ffile:
        ffile.write(labels)
    labels = "RecordName,ObsNum,P,B,V,AVG_OBS2ADC_Distance,Speed_Below_Limit,ADC2LaneBound_Distance,FastAccl,HardBrake\n"
    with open(ga_file, 'a+') as gfile:
        gfile.write(labels)
    labels = "RecordName,Simulation,Oracles,MISC,E2E,RetryNo\n"
    with open(timer_file, 'a+') as tfile:
        tfile.write(labels)
    # os.system("rm -rf /apollo/apollo_v7_testing/grading_metrics/Safety_Violations/*")


def cyber_env_init():
    cmd = f"docker exec -d {get_container_name()} bash /apollo/scripts/bootstrap.sh restart"
    subprocess.run(cmd.split())
    # os.system("bash /apollo/scripts/bootstrap.sh restart")
    time.sleep(1)

    cmd = f"docker exec -d {get_container_name()} bash /apollo/apollo_v7_testing/auxiliary/modules/start_modules.sh"
    subprocess.run(cmd.split())
    # os.system("bash /apollo/apollo_v7_testing/auxiliary/modules/start_modules.sh")
    time.sleep(10)


    # cmd = f"docker exec -d {get_container_name()} bazel run //apollo_v7_testing:toggle_sim_control"
    # subprocess.run(cmd.split())
    # sim_control_cmd_output = subprocess.check_output(sim_control_cmd, shell=True)
    run_sim_control()
    time.sleep(1)

    cmd = f"docker exec -d {get_container_name()} source /apollo/cyber/setup.bash"
    subprocess.run(cmd.split())
    # os.system("source /apollo/cyber/setup.bash")
    time.sleep(1)


def scenario_runner():
    cyber_env_init()
    pop_pickle_dump_data_path = f"{APOLLO_ROOT}/modules/tools/perception/pop_pickle/" + map_name + "_dump_data"
    # pop_pickle_dump_data_path = "/apollo/modules/tools/perception/pop_pickle/" + map_name + "_dump_data"
    pop_pickle_dump_data_file = open(pop_pickle_dump_data_path, "rb")
    creator.create("MultiFitness", base.Fitness, weights=(-1.0, -1.0, -1.0, 1.0, -1.0))
    creator.create("Individual", list, fitness=creator.MultiFitness)
    pop = pickle.load(pop_pickle_dump_data_file)

    scenario_counter = 0
    obs_group_folders_name_list = os.listdir(obs_folder)
    for obs_group_folder_name in obs_group_folders_name_list:
        obs_files_name_list = os.listdir(obs_folder + obs_group_folder_name)

        deme = pop[scenario_counter]

        start_time = time.time()
        # record_name="Generation{}_Scenario{}".format(generation,scenario_counter)
        record_name = "scenario_" + str(scenario_counter)

        e2e_time_start = time.time()
        lanes, min_distance, speeding_min, uslc_min, fastAccl_min, hardBrake_min, sim_time, orcle_time, num_runs = runScenario(
            deme, record_name, obs_group_number=scenario_counter)
        e2e_time = time.time() - e2e_time_start
        misc_time = e2e_time - sim_time - orcle_time
        scenario_counter += 1


def adc_routing_generating():
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


def runScenario(deme, record_name, obs_group_number):
    failed = True
    num_runs = 0
    # scenario_counter=0

    while failed:
        # ------- running the scneario -------
        # bazel-bin/apollo_v7_testing/scenario_player/run_automation -rv 586115.2216681268,4140677.470931069,586131.4210111903,4140791.3412697404 -o scenario_0 -mn sunnyvale_loop -ogn 0
        # scenario_player_cmd='bazel run //apollo_v7_testing/scenario_player:run_automation -- -rv 586855.34,4140800.88,587283.52,4140882.30'+' -o '+record_name+' -mn '+map_name+' -ogn '+str(obs_group_number)
        scenario_player_cmd = 'bazel run //apollo_v7_testing/scenario_player:run_automation -- -rv 586980.86,4140959.45,587283.52,4140882.30' + ' -o ' + record_name + ' -mn ' + map_name + ' -ogn ' + str(
            obs_group_number)
        # scenario_player_cmd='bazel run //apollo_v7_testing/scenario_player:run_automation -- -rv 586855.34,4140800.88,586980.86,4140959.45'+' -o '+record_name+' -mn '+map_name+' -ogn '+str(obs_group_number)

        # adc_routing = adc_routing_generating()
        # scenario_player_cmd = 'bazel run //apollo_v7_testing/scenario_player:run_automation -- -rv ' + adc_routing + ' -o ' + record_name + ' -mn ' + map_name + ' -ogn ' + str(obs_group_number)

        # cmd = f"docker exec -d {get_container_name()} "+ scenario_player_cmd
        # subprocess.run(cmd.split())

        scenario_player_output = subprocess.check_output(scenario_player_cmd, shell=True)










        scenario_player_output = str(scenario_player_output)[2:-3]

        num_runs = num_runs + 1

        # if the adc didn't move or the adc was travelling outside the map boundaries, then re-run scenrio with new routing info
        if scenario_player_output == 'None':
            continue
        scenario_player_output = scenario_player_output.split('\\n')
        min_distance = eval(scenario_player_output[0])

        # the return number of obstacles must match the ones in the individual
        # if len(min_distance) != len(deme):
        if len(min_distance) != len(deme):
            continue
        else:
            print("--------------------------------------------------")
            print(scenario_player_output)
            print("--------------------------------------------------")
            failed = False

    # scenario_counter+=1
    # scenario run successfully
    sim_time = float(scenario_player_output[8]) * num_runs
    orcle_time = float(scenario_player_output[9]) * num_runs
    lanes, min_distance, speeding_min, uslc_min, fastAccl_min, hardBrake_min = runOracles(scenario_player_output,
                                                                                          record_name, deme)
    return lanes, min_distance, speeding_min, uslc_min, fastAccl_min, hardBrake_min, sim_time, orcle_time, num_runs


if __name__ == "__main__":
    scenario_runner()
    # runScenario()
