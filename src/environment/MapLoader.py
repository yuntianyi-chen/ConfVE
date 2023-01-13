import os
import pickle
from tools.hdmap.MapParser import MapParser
from config import HD_MAP_PATH, MAP_DATA_PATH


class MapLoader:

    def __init__(self):
        self.load_map_data()

    def save_map_data(self):
        mp = MapParser(HD_MAP_PATH)
        with open(MAP_DATA_PATH, 'wb') as f:
            pickle.dump(mp, f, protocol=4)

    def load_map_data(self):
        if not os.path.exists(MAP_DATA_PATH):
            self.save_map_data()
        with open(MAP_DATA_PATH, 'rb') as f:
            map_data = pickle.load(f)
        map_data.load_instance()
        return map_data
