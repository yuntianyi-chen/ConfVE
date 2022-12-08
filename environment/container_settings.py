import pickle

from tools.hdmap.MapParser import MapParser
from config import HD_MAP_PATH, MAP_DATA_PATH


def init_settings():
    # mp = MapParser(HD_MAP_PATH)
    mp = load_map_data()


def save_map_data():
    mp = MapParser(HD_MAP_PATH)
    with open(MAP_DATA_PATH, 'wb') as f:
        pickle.dump(mp, f, protocol=4)


def load_map_data():
    with open(MAP_DATA_PATH, 'rb') as f:
        map_data = pickle.load(f)
    map_data.load_instance()
    return map_data


def get_container_name():
    return "apollo_dev_cloudsky"


if __name__ == '__main__':
    save_map_data()
    # init_settings()
