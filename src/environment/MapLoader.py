import os
import pickle
from tools.hdmap.MapParser import MapParser
from config import HD_MAP_PATH, MAP_DATA_PATH, PROJECT_ROOT


class MapLoader:

    def __init__(self, map_name=''):
        if map_name == '':
            self.hd_map_path = HD_MAP_PATH
            self.map_data_path = MAP_DATA_PATH
        else:
            self.hd_map_path = f'{PROJECT_ROOT}/data/maps/{map_name}/base_map.bin'
            self.map_data_path = f'{PROJECT_ROOT}/data/maps/{map_name}/map_pickle_data'

        if not os.path.exists(self.map_data_path):
            self.save_map_data()

        self.map_instance = self.load_map_data()

    def save_map_data(self):
        mp = MapParser(self.hd_map_path)
        with open(self.map_data_path, 'wb') as f:
            pickle.dump(mp, f, protocol=4)

    def load_map_data(self):
        with open(self.map_data_path, 'rb') as f:
            map_data = pickle.load(f)
        map_data.load_instance()
        return map_data
