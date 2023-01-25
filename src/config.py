"""
Global configurations for the framework
"""

###
# routing request message.header.module name
# different for different AV_TESTING_APPROACH
###

# IMPORTANT CONFIGURATION
OBS_PERCEPTION_FREQUENCY = 25  # 10/25
MAX_RECORD_TIME = 30  # 10/30
AV_TESTING_APPROACH = "DoppelTest"  # scenoRITA/DoppelTest/AV-Fuzzer/ADFuzz/Random
MAP_NAME = "borregas_ave"  # borregas_ave/sunnyvale_loop/San_Francisco

CONTAINER_NUM = 5  # 5/10
SIMILARITY_THRESHOLD = 0.5

MODULE_ORACLES = ["RoutingFailure", "PredictionFailure", "PlanningFailure", "CarNeverMoved", "SimControlFailure",
                  "PlanningGeneratesGarbage"]

MAX_INITIAL_SCENARIOS = 10  # 10

# t-way testing
T_STRENGTH_VALUE = 2  # pairwise
TIME_THRESHOLD = 20  # hours

# Rerun 5 times if occurred >= 3 times, confirmed
DETERMINISM_RERUN_TIMES = 5  # 5/10
DEFAULT_DETERMINISM_RERUN_TIMES = 10  # 10
DETERMINISM_CONFIRMED_TIMES = 3  # 3

# APOLLO SETTINGS
TRAFFIC_LIGHT_FREQUENCY = 10
TRAFFIC_LIGHT_MODE = "read"  # read/random/off

# TESTING SETTINGS
OPT_MODE = "GA"  # GA/DRL/Random/MIT/T-way
MODULE_NAME = "planning"
DEFAULT_CONFIG_FILE = False
CONFIG_FILE_NAME = f"{MODULE_NAME}_config.pb.txt"

# GA SETTINGS
GENERATION_LIMIT = 10
INIT_POP_SIZE = 10  # 60 individuals in each generation
FITNESS_MODE = "multi_obj"  # emerge/multi_obj
SELECT_MODE = "nsga2"  # nsga2/ratio
# FOR RATIO SELECT
SELECT_NUM_RATIO = [7, 2, 1]  # [5, 3, 2]/[7, 2, 1]



# DIRECTORIES
APOLLO_ROOT = '/home/cloudsky/Research/Apollo/apollo_v7_deploy'  # apollo_v7_deploy/apollo_7.0
PROJECT_ROOT = '/home/cloudsky/Research/Apollo/AV_Config_Testing'
RECORDS_DIR = f'{PROJECT_ROOT}/data/records'
FEATURES_CSV_DIR = f'{PROJECT_ROOT}/data/violation_features'
APOLLO_RECORDS_DIR = f'{APOLLO_ROOT}/records'
OBS_DIR = f"{APOLLO_ROOT}/modules/tools/perception/obstacles/{MAP_NAME}/"
BACKUP_SAVE_DIR = f"/home/cloudsky/Research/Apollo/Backup/{AV_TESTING_APPROACH}"
BACKUP_CONFIG_SAVE_DIR = f"{BACKUP_SAVE_DIR}/config_files/{MAP_NAME}"
BACKUP_RECORD_SAVE_DIR = f"{BACKUP_SAVE_DIR}/records/{MAP_NAME}"
INITIAL_SCENARIO_RECORD_DIR = f"{BACKUP_RECORD_SAVE_DIR}/initial"
DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR = f"{BACKUP_RECORD_SAVE_DIR}/initial_default_rerun"
MAP_DIR = f'{PROJECT_ROOT}/data/maps/{MAP_NAME}'
MY_SCRIPTS_DIR = f"{APOLLO_ROOT}/scripts/my_scripts"

# FILE PATH
FLAGFILE_PATH = f"{APOLLO_ROOT}/modules/common/data/global_flagfile.txt"
MANUAL_ADC_ROUTE_PATH = f"{PROJECT_ROOT}/data/analysis/{AV_TESTING_APPROACH}/adc_route.csv"
DEFAULT_CONFIG_FILE_PATH = f"{PROJECT_ROOT}/data/config_files/{MODULE_NAME}/conf/{CONFIG_FILE_NAME}"
CURRENT_CONFIG_FILE_PATH = f"{APOLLO_ROOT}/modules/{MODULE_NAME}/conf/{CONFIG_FILE_NAME}"
HD_MAP_PATH = f'{MAP_DIR}/base_map.bin'
MAP_DATA_PATH = f'{MAP_DIR}/map_pickle_data'

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
