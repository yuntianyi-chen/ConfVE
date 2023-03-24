from pathlib import Path

"""
Global configurations for the framework
"""

#######################
## Customized Config ##
#######################

OBS_PERCEPTION_FREQUENCY = 10
MAX_RECORD_TIME = 30  # 10/30
AV_TESTING_APPROACH = "DoppelTest"  # scenoRITA/DoppelTest/AVFuzzer/ADFuzz
MAP_NAME = "sunnyvale_loop"  # borregas_ave/sunnyvale_loop/San_Francisco/san_mateo
CONTAINER_NUM = 5  # 5/10
OPT_MODE = "T-way"  # GA/DRL/Random/T-way/OneEnabled/PreAnalyze
TIME_HOUR_THRESHOLD = 10  # hours

####################
## Default Config ##
####################

# t-way testing
T_STRENGTH_VALUE = 2  # pairwise

ONEENABLED_NUM_TYPE_TEST_TIMES = 10

# TESTING SETTINGS
MODULE_NAME = "planning"
CONFIG_FILE_NAME = f"{MODULE_NAME}_config.pb.txt"
SIMILARITY_THRESHOLD = 0.5
MAX_INITIAL_SCENARIOS = 10  # 10
IS_CUSTOMIZED_EPSILON = False
EPSILON_THRESHOLD = 1

# APOLLO SETTINGS
TRAFFIC_LIGHT_FREQUENCY = 10
DEFAULT_CONFIG_FILE = False
TRAFFIC_LIGHT_MODE = "read"  # read/random/off

# GA SETTINGS
GENERATION_LIMIT = 100  # 10/20/50
POP_SIZE = 20
OFFSPRING_SIZE = 20
# INIT_POP_SIZE = POP_SIZE + OFFSPRING_SIZE
CX_P = 0.2
MUT_P = 0.8
FITNESS_MODE = "multi_obj"  # emerge/multi_obj
SELECT_MODE = "nsga2"  # nsga2/ratio

# FOR RATIO SELECT
SELECT_NUM_RATIO = [7, 2, 1]  # [5, 3, 2]/[7, 2, 1]

# Rerun 5 times if occurred >= 3 times, confirmed
DETERMINISM_RERUN_TIMES = 5  # 5/10
DEFAULT_DETERMINISM_RERUN_TIMES = 10  # 10/30
DETERMINISM_CONFIRMED_TIMES = 4  # >3/(1+5) or >= 4/(1+5)
ENABLE_STRICT_DETERMINISM_CHECKING = True

MODULE_ORACLES = ["RoutingFailure",
                  "PredictionFailure",
                  "PlanningFailure",
                  "CarNeverMoved",
                  "SimControlFailure",
                  "PlanningGeneratesGarbage",
                  "ModuleDelayOracle"]

# INITIAL_EXP_NAME = f"{AV_TESTING_APPROACH}_{MAP_NAME}_{MAX_RECORD_TIME}"
INITIAL_EXP_NAME = f"{AV_TESTING_APPROACH}_{MAP_NAME}"
EXP_NAME_OPT_MODE = f"{INITIAL_EXP_NAME}_{OPT_MODE}"

# DIRECTORIES
DIR_ROOT = str(Path(__file__).parent.parent.parent)
PROJECT_ROOT = str(Path(__file__).parent.parent)
APOLLO_ROOT = f'{DIR_ROOT}/apollo_v7_deploy'  # apollo_v7_deploy/apollo_7.0/AV_Config_Testing

RECORDS_DIR = f'{PROJECT_ROOT}/data/records'
FEATURES_CSV_DIR = f'{PROJECT_ROOT}/data/violation_features'
APOLLO_RECORDS_DIR = f'{APOLLO_ROOT}/records'
OBS_DIR = f"{APOLLO_ROOT}/modules/tools/perception/obstacles/{MAP_NAME}"
EXP_GROUP_NAMING_TREE = f"{AV_TESTING_APPROACH}/{EXP_NAME_OPT_MODE}"
EXP_BASE_DIR = f"{PROJECT_ROOT}/data/exp_results/{EXP_GROUP_NAMING_TREE}"

# INITIAL_SCENARIO_RECORD_DIR = f"{DIR_ROOT}/Backup/initial/{INITIAL_EXP_NAME}"
INITIAL_SCENARIO_RECORD_DIR = f"{APOLLO_ROOT}/initial/{INITIAL_EXP_NAME}"
REPLAY_SCENARIO_RECORD_DIR = f"/apollo/initial/{INITIAL_EXP_NAME}"

BACKUP_SAVE_DIR = f'{DIR_ROOT}/Backup/{EXP_GROUP_NAMING_TREE}'
BACKUP_CONFIG_SAVE_DIR = f"{BACKUP_SAVE_DIR}/config_files"
BACKUP_RECORD_SAVE_DIR = f"{BACKUP_SAVE_DIR}/records"
# INITIAL_SCENARIO_RECORD_DIR = f"{BACKUP_RECORD_SAVE_DIR}/initial"
DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR = f"{BACKUP_RECORD_SAVE_DIR}/initial_default_rerun"
MAP_DIR = f'{PROJECT_ROOT}/data/maps/{MAP_NAME}'
MY_SCRIPTS_DIR = f"{APOLLO_ROOT}/scripts/my_scripts"
APOLLO_MAP_DATA_DIR = f"{APOLLO_ROOT}/modules/map/data"

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

# OBS_TYPE_DICT = {3: "PEDESTRIAN", 4: "BICYCLE", 5: "VEHICLE"}
