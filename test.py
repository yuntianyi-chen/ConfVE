import pickle
import shutil
from datetime import date
from os import listdir

from config import APOLLO_RECORDS_DIR, DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR, INITIAL_SCENARIO_RECORD_DIR

# from config import MAGGIE_ROOT
#
# ind_list_pickle_dump_data_path = f"{MAGGIE_ROOT}/data/pop_pickle/ind_list_2022-12-06"
#
# with open(ind_list_pickle_dump_data_path, 'rb') as f:
#     data = pickle.load(f)
#     print()

a = listdir(INITIAL_SCENARIO_RECORD_DIR)
a.sort()

print()

