import os
import warnings
import numpy as np
import pandas as pd
from kneed import KneeLocator
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from config import FEATURES_CSV_DIR, MODULE_ORACLES, IS_CUSTOMIZED_EPSILON, EPSILON_THRESHOLD

from matplotlib import pyplot as plt

warnings.filterwarnings('ignore')


class Eliminator:

    def __init__(self):
        # self.scaler = StandardScaler()
        self.scaler = MinMaxScaler()

    def cluster(self, pd_data):
        pd_features = pd_data.iloc[:, :]
        # pd_features = pd_data.iloc[:, 1:]
        pd_features_scaled = self.scaler.fit_transform(pd_features)
        neigh = NearestNeighbors(n_neighbors=2)
        nbrs = neigh.fit(pd_features_scaled)
        distances, indices = nbrs.kneighbors(pd_features_scaled)
        sorted_distances = np.sort(distances, axis=0)
        sorted_distances = sorted_distances[:, 1]

        # plt.plot(distances)
        # plt.show()

        i = np.arange(len(sorted_distances))
        knee = KneeLocator(i, sorted_distances, S=1, curve='convex', direction='increasing', interp_method='polynomial')
        # plt.show()
        # elbow = KneeLocator(i, distances, S=1, curve='concave', direction='increasing', interp_method='polynomial')

        if IS_CUSTOMIZED_EPSILON:
            epsilon = EPSILON_THRESHOLD
            # if knee.knee:
            #     original_epsilon = sorted_distances[knee.knee]
            # else:
            #     original_epsilon = sorted_distances[round(len(sorted_distances) / 2)]
        else:
            if knee.knee:
                epsilon = sorted_distances[knee.knee]
            else:
                epsilon = sorted_distances[round(len(sorted_distances) / 2)]

            # if knee.knee:
            #     original_epsilon = sorted_distances[knee.knee]
            # else:
            #     original_epsilon = sorted_distances[round(len(sorted_distances) / 2)]

        if epsilon != 0:
            # Cluster the features based on eps
            db_clusters = DBSCAN(eps=epsilon, min_samples=1, metric='euclidean').fit_predict(pd_features_scaled)
        else:
            db_clusters = [0 for i in range(len(pd_data))]
        # print(db_clusters)
        num_clusters = len(set(db_clusters))
        all_vio = len(pd_features_scaled)
        unique_vio = num_clusters
        elim_ratio = 100 * (1 - float(num_clusters) / len(pd_features_scaled))
        # message = csv_file_name + ',  {:,},  {:,},  {:.2f}%'
        # print(message.format(all_vio, unique_vio, elim_ratio))

        # self.analyze_vio(db_clusters, epsilon, distances)
        return db_clusters, all_vio, unique_vio, elim_ratio

    def analyze_vio(self, db_clusters, epsilon, distances):
        cluster_id = db_clusters[-1]
        if cluster_id not in db_clusters[:-1]:
            check_similar = False
        else:
            check_similar = True
        print(f"epsilon: {epsilon} vs. distance: {distances[-1][-1]} -> Emerged: {not check_similar}")


if __name__ == "__main__":
    target_approach = "all"  # GA/T-way
    # target_name = "scenoRITA_san_mateo_10_T-way"  # borregas_ave_30s/sunnyvale_loop_10s/scenoRITA_san_mateo_10_GA

    target_name_list = ["scenoRITA_borregas_ave_GA", "scenoRITA_borregas_ave_T-way", "scenoRITA_san_mateo_GA",
                        "scenoRITA_san_mateo_T-way", "scenoRITA_sunnyvale_loop_GA",
                        "scenoRITA_sunnyvale_loop_T-way",
                        "DoppelTest_borregas_ave_GA", "DoppelTest_borregas_ave_T-way",
                        "DoppelTest_san_mateo_GA",
                        "DoppelTest_san_mateo_T-way",
                        "DoppelTest_sunnyvale_loop_GA",
                        "DoppelTest_sunnyvale_loop_T-way",
                        "ADFuzz_borregas_ave_GA", "ADFuzz_borregas_ave_T-way",
                        "AV-Fuzzer_San_Francisco_GA", "AV-Fuzzer_San_Francisco_T-way"]
    approach_list = ["scenoRITA", "DoppelTest", "ADFuzz", "AV-Fuzzer"]
    oracle_list = ["CollisionOracle.csv", "AccelOracle.csv", "DecelOracle.csv", "SpeedingOracle.csv",
                   "UnsafeLaneChangeOracle.csv",
                   "ModuleDelayOracle.csv", "PlanningFailure.csv", "PlanningGeneratesGarbage.csv",
                   "JunctionLaneChangeOracle.csv", "StopSignOracle.csv", "TrafficSignalOracle.csv", "EStopOracle.csv"]
    map_list = ["borregas_ave", "san_mateo", "sunnyvale_loop", "San_Francisco"]

    output_oracle_list = ["Collision", "Fast Acceleration", "Hard Braking", "Speeding", "Unsafe Lane Change",
                          "Module Delay", "Module Malfunction", "Module Illness", "Lane-change in Junction",
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
        oracle_all_list = []
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
                        db_clusters, all_vio, unique_vio, elim_ratio = eliminator.cluster(pd_data)
                        pd_data.insert(0, "clusters", db_clusters, True)
                        message = oracle_type + ',  {:,},  {:,},  {:.2f}%'
                        print(message.format(all_vio, unique_vio, elim_ratio))
                        pd_data.to_csv(output_file_path, index=False)
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
    df_unique_pairwise_final = df_unique_final[[name for name in df_unique_final.columns if "T-way" in name]]

    df_elim = pd.DataFrame()
    for approach_name in approach_list:
        df_elim[f"{approach_name}_All"] = df_all_GA_final[
            [name for name in df_all_GA_final.columns if approach_name in name]].sum(axis=1)
        df_elim[f"{approach_name}_Unique"] = df_unique_GA_final[
            [name for name in df_unique_GA_final.columns if approach_name in name]].sum(axis=1)
        df_elim[f"{approach_name}_Elim."] = (
                (1 - df_elim[f"{approach_name}_Unique"] / df_elim[f"{approach_name}_All"]) * 100).round(2)

    dr_ga_map = pd.DataFrame()
    for approach_name in approach_list:
        temp_df = df_unique_GA_final[[name for name in df_unique_GA_final.columns if approach_name in name]]
        dr_ga_map = pd.concat([dr_ga_map, temp_df], axis=1)

    df_map_ga_pairwise = pd.DataFrame()
    for map_name in map_list:
        temp1_df = df_unique_GA_final[[name for name in df_unique_GA_final.columns if map_name in name]].sum(axis=1)
        temp2_df = df_unique_pairwise_final[
            [name for name in df_unique_pairwise_final.columns if map_name in name]].sum(axis=1)
        df_map_ga_pairwise = pd.concat([df_map_ga_pairwise, temp1_df, temp2_df], axis=1)

    df_ads_ga_pairwise = pd.DataFrame()
    for approach_name in approach_list:
        temp1_df = df_unique_GA_final[[name for name in df_unique_GA_final.columns if approach_name in name]].sum(
            axis=1)
        temp2_df = df_unique_pairwise_final[
            [name for name in df_unique_pairwise_final.columns if approach_name in name]].sum(axis=1)
        df_ads_ga_pairwise = pd.concat([df_ads_ga_pairwise, temp1_df, temp2_df], axis=1)

    with open(f"{FEATURES_CSV_DIR}/latex.txt", "w") as f:

        f.write("all ads/GA_pairwise\n")
        for index, row in df_unique_final.iterrows():
            f.write("\\textbf{" + output_oracle_list[index] + "}")
            write_str = ""
            pair = []
            for a_num in row:
                pair.append(a_num)
                if len(pair) == 2:
                    if pair[0] > pair[1]:
                        pair[0] = "\\textbf{" + str(pair[0]) + "}"
                    elif pair[0] < pair[1]:
                        pair[1] = "\\textbf{" + str(pair[1]) + "}"
                    write_str += f" & {pair[0]} & {pair[1]}"
                    pair = []
            f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")

        f.write("elim by ads\n")
        for idx in df_elim.index:
            f.write("\\textbf{" + output_oracle_list[idx] + "} ")
            write_str = ""
            for col in df_elim.columns:
                value = str(df_elim.loc[idx, col])
                if "Elim." in col:
                    if value != "nan":
                        write_item = format(df_elim.loc[idx, col], ".2f") + "\%"
                    else:
                        write_item = "/"
                else:
                    write_item = value
                write_str += f"& {write_item} "
            f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")

        f.write("by ga map\n")
        for index, row in dr_ga_map.iterrows():
            f.write("\\textbf{" + output_oracle_list[index] + "}")
            write_str = ""
            for a_num in row:
                write_str += f" & {a_num}"
            f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")

        f.write("by map ga_pairwise\n")
        for index, row in df_map_ga_pairwise.iterrows():
            f.write("\\textbf{" + output_oracle_list[index] + "}")
            write_str = ""
            pair = []
            for a_num in row:
                pair.append(a_num)
                if len(pair) == 2:
                    if pair[0] > pair[1]:
                        pair[0] = "\\textbf{" + str(pair[0]) + "}"
                    elif pair[0] < pair[1]:
                        pair[1] = "\\textbf{" + str(pair[1]) + "}"
                    write_str += f" & {pair[0]} & {pair[1]}"
                    pair = []
            f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")

        f.write("by ads ga_pairwise\n")
        for index, row in df_ads_ga_pairwise.iterrows():
            f.write("\\textbf{" + output_oracle_list[index] + "}")
            write_str = ""
            pair = []
            for a_num in row:
                pair.append(a_num)
                if len(pair) == 2:
                    if pair[0] > pair[1]:
                        pair[0] = "\\textbf{" + str(pair[0]) + "}"
                    elif pair[0] < pair[1]:
                        pair[1] = "\\textbf{" + str(pair[1]) + "}"
                    write_str += f" & {pair[0]} & {pair[1]}"
                    pair = []
            f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")
