import pickle
from datetime import date


# from config import MAGGIE_ROOT
#
# ind_list_pickle_dump_data_path = f"{MAGGIE_ROOT}/data/pop_pickle/ind_list_2022-12-06"
#
# with open(ind_list_pickle_dump_data_path, 'rb') as f:
#     data = pickle.load(f)
#     print()

class AA:
    def __init__(self):
        self.aa = None


a = [123, 444, [34]]

zxc = AA()
bb=AA()

zxc.aa = a
bb.aa=a
print(zxc.aa)

a[0]="asd"
print(zxc.aa)
print(bb.aa)
