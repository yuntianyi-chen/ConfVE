"""
Global configurations for the framework
"""

import logging

# APOLLO CONFIGURATION ==============================
PERCEPTION_FREQUENCY = 25  # used to be 25
TRAFFIC_LIGHT_FREQUENCY = 10
MAX_RECORD_TIME = 30   # 10
AV_TESTING_APPROACH = "DoppelTest"    # scenoRITA/DoppelTest/AV-Fuzzer/ADFuzz/Random
MAP_NAME = "borregas_ave"   # borregas_ave/sunnyvale_loop
TRAFFIC_LIGHT_MODE = "read"  # read/random/off
########################



GENERATION_LIMIT = 10
INIT_POP_SIZE = 10  # 60 individuals in each generation
SELECT_NUM_RATIO = [7, 2, 1]  # [5, 3, 2]

# MAX_RECORD_TIME = 3
# INIT_POP_SIZE = 3
# SELECT_NUM_RATIO = [1, 1, 1]

SAVE_RECORD = False

APOLLO_VEHICLE_LENGTH = 4.933
APOLLO_VEHICLE_WIDTH = 2.11
APOLLO_VEHICLE_HEIGHT = 1.48
APOLLO_VEHICLE_back_edge_to_center = 1.043


########################

# CONFIG_TESTING_MODE = False
# OBS_GENERATE_MODE = "scenoRITA"
MODULE_NAME = "planning"
DEFAULT_CONFIG_FILE = False
SCENARIO_GENERATION_MODE = True


OPTIMAL_IND_LIST_LENGTH = 30



OBS_GROUP_COUNT = 10
# FITNESS_MODE = "intro_remov"  # or accu_vio_num
FITNESS_MODE = "intro"  # or accu_vio_num

# DIRECTORIES =======================================
APOLLO_ROOT = '/home/cloudsky/Research/Apollo/apollo_7.0'
MAGGIE_ROOT = '/home/cloudsky/Research/Apollo/AV_Config_Testing'
RECORDS_DIR = f'{MAGGIE_ROOT}/data/records'
APOLLO_RECORDS_DIR = f'{APOLLO_ROOT}/records'
LOG_DIR = f'{MAGGIE_ROOT}/data/Logs'
CSV_DIR = f'{MAGGIE_ROOT}/data/csv'
# OBS_DIR = f"{APOLLO_ROOT}/modules/tools/perception/obstacles/{MAP_NAME}/obs_in_group"
OBS_DIR = f"{APOLLO_ROOT}/modules/tools/perception/obstacles/{MAP_NAME}/"

# PATH ====================================
ADC_ROUTE_PATH = f"{MAGGIE_ROOT}/data/analysis/{AV_TESTING_APPROACH}/adc_route.csv"
VIO_NUM_PATH = f"{MAGGIE_ROOT}/data/analysis/{AV_TESTING_APPROACH}/vio_num.csv"
INITIAL_SCENARIO_RECORD_DIR = f"/home/cloudsky/Research/Apollo/Backup/{AV_TESTING_APPROACH}/records/initial"
DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR = f"/home/cloudsky/Research/Apollo/Backup/{AV_TESTING_APPROACH}/records/initial_default_rerun"


CONFIG_FILE_PATH=f"{APOLLO_ROOT}/modules/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"

BACKUP_CONFIG_SAVE_PATH = f"/home/cloudsky/Research/Apollo/Backup/{AV_TESTING_APPROACH}/config_files"
BACKUP_RECORD_SAVE_PATH = f"/home/cloudsky/Research/Apollo/Backup/{AV_TESTING_APPROACH}/records"
# MAGGIE CONFIGS ====================================
STREAM_LOGGING_LEVEL = logging.INFO
USE_SIM_CONTROL_STANDALONE = True
FORCE_INVALID_TRAFFIC_CONTROL = False
SCENARIO_UPPER_LIMIT = 30
INSTANCE_MAX_WAIT_TIME = 15
MAX_ADC_COUNT = 5
MAX_PD_COUNT = 5
RUN_FOR_HOUR = 12


MAP_PATH = f'{MAGGIE_ROOT}/data/maps/{MAP_NAME}'
HD_MAP_PATH = f'{MAP_PATH}/base_map.bin'
MAP_DATA_PATH = f'{MAP_PATH}/map_pickle_data'

##################################
# Configuration Control
CONFIGURATION_REVERTING = False # Tune back after detecting violations
ENABLE_CROSSOVER = True

##################################
OPT_MODE = "GA"  # GA/DRL/Random
