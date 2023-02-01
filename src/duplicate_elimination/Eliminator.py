import os
import warnings
import numpy as np
import pandas as pd
from kneed import KneeLocator
# from matplotlib import pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from config import FEATURES_CSV_DIR, MODULE_ORACLES

warnings.filterwarnings('ignore')


class Eliminator:

    def __init__(self):
        self.scaler = StandardScaler()

    def cluster(self, pd_data, csv_file_name):
        pd_features = pd_data.iloc[:, 1:]
        # scaler = MinMaxScaler()
        pd_features_scaled = self.scaler.fit_transform(pd_features)
        neigh = NearestNeighbors(n_neighbors=2)
        nbrs = neigh.fit(pd_features_scaled)
        distances, indices = nbrs.kneighbors(pd_features_scaled)
        distances = np.sort(distances, axis=0)
        distances = distances[:, 1]
        # plt.plot(distances)
        # plt.show()
        i = np.arange(len(distances))
        knee = KneeLocator(i, distances, S=1, curve='convex', direction='increasing', interp_method='polynomial')
        # plt.show()
        if knee.knee:
            epsilon = distances[knee.knee]
        else:
            epsilon = distances[round(len(distances) / 2) - 1]
        # Cluster the features based on eps
        db_clusters = DBSCAN(eps=epsilon, min_samples=1, metric='cityblock').fit_predict(pd_features_scaled)
        num_clusters = len(set(db_clusters))

        all_vio = len(pd_features_scaled)
        unique_vio = num_clusters
        elim_ratio = 100 * (1 - float(num_clusters) / len(pd_features_scaled))
        message = csv_file_name + ',  {:,},  {:,},  {:.2f}%'
        print(message.format(all_vio, unique_vio, elim_ratio))

        pd_data.insert(0, "clusters", db_clusters, True)
        return pd_data, all_vio, unique_vio, elim_ratio


if __name__ == "__main__":
    target_approach = "all"  # GA/T-way
    # target_name = "scenoRITA_san_mateo_10_T-way"  # borregas_ave_30s/sunnyvale_loop_10s/scenoRITA_san_mateo_10_GA

    target_name_list = ["scenoRITA_borregas_ave_30_GA", "scenoRITA_borregas_ave_30_T-way", "scenoRITA_san_mateo_30_GA",
                        "scenoRITA_san_mateo_30_T-way", "scenoRITA_sunnyvale_loop_30_GA",
                        "scenoRITA_sunnyvale_loop_30_T-way",
                        "DoppelTest_borregas_ave_30_GA", "DoppelTest_borregas_ave_30_T-way",
                        "DoppelTest_san_mateo_30_GA",
                        "DoppelTest_san_mateo_30_T-way",
                        # "DoppelTest_sunnyvale_loop_30_GA",
                        # "DoppelTest_sunnyvale_loop_30_T-way",
                        "ADFuzz_borregas_ave_30_GA", "ADFuzz_borregas_ave_30_T-way",
                        "AV-Fuzzer_San_Francisco_30_GA", "AV-Fuzzer_San_Francisco_30_T-way"]
    approach_list=["scenoRITA", "DoppelTest","ADFuzz", "AV-Fuzzer"]
    oracle_list = ["CollisionOracle.csv", "AccelOracle.csv", "DecelOracle.csv", "SpeedingOracle.csv",
                   "UnsafeLaneChangeOracle.csv",
                   "ModuleDelayOracle.csv", "PlanningFailure.csv", "PlanningGeneratesGarbage.csv",
                   "JunctionLaneChangeOracle.csv", "StopSignOracle.csv", "TrafficSignalOracle.csv", "EStopOracle.csv"]

    output_oracle_list = ["Collision", "Fast Acceleration", "Hard Braking", "Speeding", "Unsafe Lane Change",
                          "Module Delay", "Module Never Works", "Module Works Wrongly", "Lane-change in Junction",
                          "Stop Sign Violation", "Traffic Signal violation", "Estop", "Total"]

    # target_name_list = os.listdir(f"{FEATURES_CSV_DIR}/{target_approach}")
    # target_name_list.sort()
    df_unique_dict = {}
    df_all_dict = {}

    for target_name in target_name_list:
        print("-----------------------------------")
        print(target_name)

        target_dir = f"{FEATURES_CSV_DIR}/{target_approach}/{target_name}/violation_features"
        csv_files_name_list = [name for name in os.listdir(target_dir) if ".csv" in name]

        output_dir = f"{target_dir}/output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print("ViolationType,  Violations No.,  Violations No.(Unique),  Elimination%")

        eliminator = Eliminator()

        oracle_unique_list = []
        oracle_all_list= []
        # oracle_elim_dict = {}

        for oracle in oracle_list:
            oracle_type = oracle.split(".")[0]

            if oracle in csv_files_name_list:

                # for csv_file_name in csv_files_name_list:
                csv_file_path = os.path.join(target_dir, oracle)
                pd_data = pd.read_csv(csv_file_path, encoding='utf-8')

                if oracle_type in MODULE_ORACLES:
                    pd_record_id = pd_data["record_id"]
                    unique = len(set(pd_record_id))
                    message = oracle + ',  {:,},  {:,},  {:.2f}%'

                    all_vio = len(pd_record_id)
                    unique_vio = unique
                    elim_ratio = 100 * (1 - float(unique) / len(pd_record_id))
                    print(message.format(all_vio, unique_vio, elim_ratio))

                else:
                    # if len(pd_data) > 5:
                    # output_file_path = f"{output_dir}/clustered_{csv_file_name}"
                    # output_data = eliminator.cluster(pd_data, csv_file_name)
                    # output_data.to_csv(output_file_path, index=False)
                    try:
                        output_file_path = f"{output_dir}/clustered_{oracle}"
                        output_data, all_vio, unique_vio, elim_ratio = eliminator.cluster(pd_data, oracle_type)
                        output_data.to_csv(output_file_path, index=False)
                    except:
                        print(f"Cannot eliminate {oracle_type}")

                oracle_unique_list.append(unique_vio)
                oracle_all_list.append(all_vio)
            else:
                oracle_unique_list.append(0)
                oracle_all_list.append(0)
        oracle_unique_list.append(sum(oracle_unique_list))
        oracle_all_list.append(sum(oracle_all_list))
        df_unique_dict[target_name] = oracle_unique_list
        if "GA" in target_name:
            df_all_dict[target_name] = oracle_all_list

    # df_dict["Total"] = sum(oracle_unique_list)

    df_unique_final = pd.DataFrame(data=df_unique_dict)
    df_all_GA_final = pd.DataFrame(data=df_all_dict)
    df_unique_GA_final = df_unique_final[[name for name in df_unique_final.columns if "GA" in name]]


    df_elim = pd.DataFrame()


    for approach_name in approach_list:
        df_elim[f"{approach_name}_All"] = df_all_GA_final[[name for name in df_all_GA_final.columns if approach_name in name]].sum(axis=1)
        df_elim[f"{approach_name}_Unique"] = df_unique_GA_final[[name for name in df_unique_GA_final.columns if approach_name in name]].sum(axis=1)
        df_elim[f"{approach_name}_Elim."] = ((1 - df_elim[f"{approach_name}_Unique"]/df_elim[f"{approach_name}_All"])*100).round(2)

    with open(f"{FEATURES_CSV_DIR}/latex.txt", "w") as f:
        for index, row in df_unique_final.iterrows():
            f.write("\\textbf{"+output_oracle_list[index]+"} ")

            write_str = ""
            pair = []
            for a_num in row:
                pair.append(a_num)
                if len(pair) == 2:
                    if pair[0] > pair[1]:
                        pair[0] = "\\textbf{"+str(pair[0])+"}"
                    elif pair[0] < pair[1]:
                        pair[1] = "\\textbf{"+str(pair[1])+"}"
                    write_str += f" & {pair[0]} & {pair[1]}"
                    pair =[]
            f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")



        for idx in df_elim.index:
            f.write("\\textbf{"+output_oracle_list[idx]+"} ")

            write_str = ""
            for col in df_elim.columns:
                value = str(df_elim.loc[idx, col])
                if "Elim." in col:
                    if value != "nan":
                        write_item = format(df_elim.loc[idx, col],".2f")+"\%"
                    else:
                        write_item = "/"
                else:
                    write_item = value
                write_str += f"& {write_item} "

            f.write(f"{write_str}\\\\ \n")


