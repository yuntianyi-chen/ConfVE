import os
import pickle
from tools.hdmap.MapParser import MapParser
from config import HD_MAP_PATH, MAP_DATA_PATH


class MapLoader:

    def __init__(self):
        self.hd_map_path = HD_MAP_PATH
        self.map_data_path = MAP_DATA_PATH

        if not os.path.exists(self.map_data_path):
            self.save_map_data()
        self.load_map_data()

    def save_map_data(self):
        mp = MapParser(self.hd_map_path)
        with open(self.map_data_path, 'wb') as f:
            pickle.dump(mp, f, protocol=4)

    def load_map_data(self):
        with open(self.map_data_path, 'rb') as f:
            map_data = pickle.load(f)
        map_data.load_instance()
        return map_data
