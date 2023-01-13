from config import OPT_MODE
from optimization_algorithms.genetic_algorithm.GARunner import GARunner

if __name__ == '__main__':
    if OPT_MODE == "GA":
        GARunner()
