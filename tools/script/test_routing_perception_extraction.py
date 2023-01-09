# init_settings()
from pandas import read_csv

from config import ADC_ROUTE_PATH, USING_PRE_RECORD_DIR
from testing_approaches.interface import extract_routing_perception_info

adc_route_csv = read_csv(ADC_ROUTE_PATH)
recordname_list = adc_route_csv['RecordName'].tolist()

violation_num_list = []

file_list = [f"{USING_PRE_RECORD_DIR}/{i}.00000" for i in recordname_list]
results_list = []
for i in file_list:
    extract_routing_perception_info(file_list)
