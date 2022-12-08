import pickle
from datetime import date

# from config import MAGGIE_ROOT
#
# ind_list_pickle_dump_data_path = f"{MAGGIE_ROOT}/data/pop_pickle/ind_list_2022-12-06"
#
# with open(ind_list_pickle_dump_data_path, 'rb') as f:
#     data = pickle.load(f)
#     print()



a={"rr":123, "dd":0}

if "asd" not in a.keys():
    a["asd"] = []
else:
    a["asd"].append("asdasd")


print(a)