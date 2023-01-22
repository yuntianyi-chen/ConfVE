import time
import pandas as pd
from duplicate_elimination.Eliminator import Eliminator



def run(eliminator):
    filename = "mut_features.csv"
    data = pd.read_csv(filename, encoding='utf-8')
    print("ViolationType,Violations No.,Violations No.(Unique),Elimination %")


    eliminator.collision(data)

    eliminator.speeding(data)

    # eliminator.unsafe_lane_change(data)

    eliminator.accel(data)
    eliminator.hardbrake(data)




if __name__ == "__main__":
    start_time=time.time()

    eliminator = Eliminator()

    run(eliminator)
    print("------------------------")
    print("Clustering time (sec.): {:.3f}".format(time.time()-start_time))
