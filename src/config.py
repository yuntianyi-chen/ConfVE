from pathlib import Path

"""
Global configurations for the framework
"""

#######################
## Customized Config ##
#######################

OBS_PERCEPTION_FREQUENCY = 10
MAX_RECORD_TIME = 30  # 10/30
CONTAINER_NUM = 5  # 5/10
TIME_HOUR_THRESHOLD = 10  # hours
AV_TESTING_APPROACH = "SCTrans"  # scenoRITA/DoppelTest/AVFuzzer/ADFuzz/SCTrans
MAP_NAME = "borregas_ave"  # borregas_ave/sunnyvale_loop/San_Francisco/san_mateo
OPT_MODE = "GA"  # GA/T-way/ConfVD
DO_RANGE_ANALYSIS = False

ADS_SELECT = "Autoware"  # Apollo/Autoware

####################
## Default Config ##
####################

# t-way testing
T_STRENGTH_VALUE = 2  # 2: pairwise

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
TRAFFIC_LIGHT_MODE = "read"

# GA SETTINGS
GENERATION_LIMIT = 100  # 10/20/50
POP_SIZE = 20
OFFSPRING_SIZE = 20
CX_P = 0.2
MUT_P = 0.8
FITNESS_MODE = "multi_obj"
SELECT_MODE = "nsga2"

# FOR RATIO SELECT
SELECT_NUM_RATIO = [7, 2, 1]

# Rerun 5 times if occurred >= 3 times, confirmed
DETERMINISM_RERUN_TIMES = 5  # 5/10
DEFAULT_DETERMINISM_RERUN_TIMES = 10  # 10/30
DETERMINISM_CONFIRMED_TIMES = 4  #
ENABLE_STRICT_DETERMINISM_CHECKING = True

MODULE_ORACLES = ["RoutingFailure",
                  "PredictionFailure",
                  "PlanningFailure",
                  "CarNeverMoved",
                  "SimControlFailure",
                  "PlanningGeneratesGarbage",
                  "ModuleDelayOracle"]

INITIAL_EXP_NAME = f"{AV_TESTING_APPROACH}_{MAP_NAME}"
EXP_NAME_OPT_MODE = f"{INITIAL_EXP_NAME}_{OPT_MODE}"

# DIRECTORIES
DIR_ROOT = str(Path(__file__).parent.parent.parent)
PROJECT_ROOT = str(Path(__file__).parent.parent)

if ADS_SELECT == "Apollo":
    ADS_ROOT = f'{DIR_ROOT}/apollo-baidu'

    FEATURES_CSV_DIR = f'{PROJECT_ROOT}/data/violation_features'
    ADS_RECORDS_DIR = f'{ADS_ROOT}/records'

    EXP_GROUP_NAMING_TREE = f"{AV_TESTING_APPROACH}/{EXP_NAME_OPT_MODE}"
    EXP_BASE_DIR = f"{PROJECT_ROOT}/data/exp_results/{EXP_GROUP_NAMING_TREE}"
    INITIAL_SCENARIO_RECORD_DIR = f"{ADS_ROOT}/initial/{INITIAL_EXP_NAME}"
    REPLAY_SCENARIO_RECORD_DIR = f"/apollo/initial/{INITIAL_EXP_NAME}"

    BACKUP_SAVE_DIR = f'{DIR_ROOT}/Backup/{EXP_GROUP_NAMING_TREE}'
    BACKUP_CONFIG_SAVE_DIR = f"{BACKUP_SAVE_DIR}/config_files"
    BACKUP_RECORD_SAVE_DIR = f"{BACKUP_SAVE_DIR}/records"
    DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR = f"{BACKUP_RECORD_SAVE_DIR}/initial_default_rerun"
    MAP_DIR = f'{PROJECT_ROOT}/data/maps/{MAP_NAME}'
    MY_SCRIPTS_DIR = f"{ADS_ROOT}/scripts/my_scripts"
    ADS_MAP_DATA_DIR = f"{ADS_ROOT}/modules/map/data"

    # FILE PATH
    FLAGFILE_PATH = f"{ADS_ROOT}/modules/common/data/global_flagfile.txt"
    DEFAULT_CONFIG_FILE_PATH = f"{PROJECT_ROOT}/data/config_files/apollo/{MODULE_NAME}/conf/{CONFIG_FILE_NAME}"
    CURRENT_CONFIG_FILE_PATH = f"{ADS_ROOT}/modules/{MODULE_NAME}/conf/{CONFIG_FILE_NAME}"
    HD_MAP_PATH = f'{MAP_DIR}/base_map.bin'
    MAP_DATA_PATH = f'{MAP_DIR}/map_pickle_data'
else:
    ADS_ROOT = f'{DIR_ROOT}/autoware'

    FEATURES_CSV_DIR = f'{PROJECT_ROOT}/data/violation_features'
    ADS_RECORDS_DIR = f'{ADS_ROOT}/records'

    EXP_GROUP_NAMING_TREE = f"{AV_TESTING_APPROACH}/{EXP_NAME_OPT_MODE}"
    EXP_BASE_DIR = f"{PROJECT_ROOT}/data/exp_results/{EXP_GROUP_NAMING_TREE}"
    INITIAL_SCENARIO_RECORD_DIR = f"{ADS_ROOT}/initial/{INITIAL_EXP_NAME}"
    # REPLAY_SCENARIO_RECORD_DIR = f"/autoware/initial/{INITIAL_EXP_NAME}"

    BACKUP_SAVE_DIR = f'{DIR_ROOT}/Backup/{EXP_GROUP_NAMING_TREE}'
    BACKUP_CONFIG_SAVE_DIR = f"{BACKUP_SAVE_DIR}/config_files"
    BACKUP_RECORD_SAVE_DIR = f"{BACKUP_SAVE_DIR}/records"
    DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR = f"{BACKUP_RECORD_SAVE_DIR}/initial_default_rerun"
    # MAP_DIR = f'{PROJECT_ROOT}/data/maps/{MAP_NAME}'
    # MY_SCRIPTS_DIR = f"{ADS_ROOT}/scripts/my_scripts"
    # AUTOWARE_MAP_DATA_DIR = f"{ADS_ROOT}/modules/map/data"

    # FILE PATH
    # FLAGFILE_PATH = f"{AUTOWARE_ROOT}/modules/common/data/global_flagfile.txt"
    AUTOWARE_DEFAULT_CONFIG_DIR_PATH = f"{PROJECT_ROOT}/data/config_files/autoware/{MODULE_NAME}"
    AUTOWARE_CURRENT_CONFIG_DIR_PATH = f"{ADS_ROOT}/src/launcher/autoware_launch/autoware_launch/config/{MODULE_NAME}"
    # HD_MAP_PATH = f'{MAP_DIR}/base_map.bin'
    # MAP_DATA_PATH = f'{MAP_DIR}/map_pickle_data'

# DOPPELTEST CONFIGS
FORCE_INVALID_TRAFFIC_CONTROL = False
SCENARIO_UPPER_LIMIT = MAX_RECORD_TIME

# VEHICLE CONFIGS
APOLLO_VEHICLE_LENGTH = 4.933
APOLLO_VEHICLE_WIDTH = 2.11
APOLLO_VEHICLE_HEIGHT = 1.48
APOLLO_VEHICLE_back_edge_to_center = 1.043
