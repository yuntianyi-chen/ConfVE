"""
Global configurations for the framework
"""


# IMPORTANT CONFIGURATION
PERCEPTION_FREQUENCY = 25  # used to be 25
TRAFFIC_LIGHT_FREQUENCY = 10
MAX_RECORD_TIME = 30  # 10
AV_TESTING_APPROACH = "DoppelTest"  # scenoRITA/DoppelTest/AV-Fuzzer/ADFuzz/Random
MAP_NAME = "borregas_ave"  # borregas_ave/sunnyvale_loop
TRAFFIC_LIGHT_MODE = "read"  # read/random/off

# Rerun 5 times if occurred >= 3 times, confirmed
DETERMINISM_RERUN_TIMES = 5
DEFAULT_DETERMINISM_RERUN_TIMES = 10
DETERMINISM_CONFIRMED_TIMES = 3

# TESTING SETTINGS
OPT_MODE = "GA"  # GA/DRL/Random
MODULE_NAME = "planning"
DEFAULT_CONFIG_FILE = False

# GA SETTINGS
GENERATION_LIMIT = 10
INIT_POP_SIZE = 10  # 60 individuals in each generation
SELECT_NUM_RATIO = [7, 2, 1]  # [5, 3, 2]
FITNESS_MODE = "emerge"  # emerge/emerge_and_removal

# DIRECTORIES
APOLLO_ROOT = '/home/cloudsky/Research/Apollo/apollo_7.0'
PROJECT_ROOT = '/home/cloudsky/Research/Apollo/AV_Config_Testing'
RECORDS_DIR = f'{PROJECT_ROOT}/data/records'
APOLLO_RECORDS_DIR = f'{APOLLO_ROOT}/records'
OBS_DIR = f"{APOLLO_ROOT}/modules/tools/perception/obstacles/{MAP_NAME}/"
INITIAL_SCENARIO_RECORD_DIR = f"/home/cloudsky/Research/Apollo/Backup/{AV_TESTING_APPROACH}/records/initial"
DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR = f"/home/cloudsky/Research/Apollo/Backup/{AV_TESTING_APPROACH}/records/initial_default_rerun"
BACKUP_CONFIG_SAVE_DIR = f"/home/cloudsky/Research/Apollo/Backup/{AV_TESTING_APPROACH}/config_files"
BACKUP_RECORD_SAVE_DIR = f"/home/cloudsky/Research/Apollo/Backup/{AV_TESTING_APPROACH}/records"
MAP_DIR = f'{PROJECT_ROOT}/data/maps/{MAP_NAME}'
MY_SCRIPTS_DIR = f"{APOLLO_ROOT}/scripts/my_scripts"

# FILE PATH
MANUAL_ADC_ROUTE_PATH = f"{PROJECT_ROOT}/data/analysis/{AV_TESTING_APPROACH}/adc_route.csv"
DEFAULT_CONFIG_FILE_PATH = f"{PROJECT_ROOT}/data/config_files/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
CURRENT_CONFIG_FILE_PATH = f"{APOLLO_ROOT}/modules/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
HD_MAP_PATH = f'{MAP_DIR}/base_map.bin'
MAP_DATA_PATH = f'{MAP_DIR}/map_pickle_data'

########################
# For randomly generating scenarios
OBS_GROUP_COUNT = 10

# DOPPELTEST CONFIGS
FORCE_INVALID_TRAFFIC_CONTROL = False
SCENARIO_UPPER_LIMIT = MAX_RECORD_TIME

#######################
APOLLO_VEHICLE_LENGTH = 4.933
APOLLO_VEHICLE_WIDTH = 2.11
APOLLO_VEHICLE_HEIGHT = 1.48
APOLLO_VEHICLE_back_edge_to_center = 1.043


OBS_TYPE_DICT = {3: "PEDESTRIAN", 4: "BICYCLE", 5: "VEHICLE"}
