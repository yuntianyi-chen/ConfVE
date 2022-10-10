"""
Global configurations for the framework
"""

import logging

# APOLLO CONFIGURATION ==============================
PERCEPTION_FREQUENCY = 25

MAX_RECORD_TIME = 10

APOLLO_VEHICLE_LENGTH = 4.933
APOLLO_VEHICLE_WIDTH = 2.11
APOLLO_VEHICLE_HEIGHT = 1.48
APOLLO_VEHICLE_back_edge_to_center = 1.043

MAP_NAME = "sunnyvale_loop"
MODULE_NAME = "planning"
DEFAULT_CONFIG_FILE = True

# DIRECTORIES =======================================
APOLLO_ROOT = '/home/cloudsky/Research/Apollo/apollo_7.0'
MAGGIE_ROOT = '/home/cloudsky/Research/Apollo/AV_Config_Testing'
RECORDS_DIR = f'{MAGGIE_ROOT}/data/records'
LOG_DIR = f'{MAGGIE_ROOT}/data/Logs'
CSV_DIR = f'{MAGGIE_ROOT}/data/csv'

OBS_DIR = f"{APOLLO_ROOT}/modules/tools/perception/obstacles/{MAP_NAME}/"

# MAGGIE CONFIGS ====================================
STREAM_LOGGING_LEVEL = logging.INFO
USE_SIM_CONTROL_STANDALONE = True
FORCE_INVALID_TRAFFIC_CONTROL = False
SCENARIO_UPPER_LIMIT = 30
INSTANCE_MAX_WAIT_TIME = 15
MAX_ADC_COUNT = 5
MAX_PD_COUNT = 5
RUN_FOR_HOUR = 12
HD_MAP_PATH = f'{MAGGIE_ROOT}/data/maps/{MAP_NAME}/base_map.bin'
