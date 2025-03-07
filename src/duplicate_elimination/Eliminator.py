import os
import warnings
import numpy as np
import pandas as pd
from kneed import KneeLocator
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from config import FEATURES_CSV_DIR, MODULE_ORACLES, IS_CUSTOMIZED_EPSILON, EPSILON_THRESHOLD
from duplicate_elimination.LatexGenerator import LatexGenerator

warnings.filterwarnings('ignore')


class Eliminator:
    def __init__(self):
        self.scaler = MinMaxScaler()

    def cluster(self, pd_features):
        pd_features_scaled = self.scaler.fit_transform(pd_features)
        neigh = NearestNeighbors(n_neighbors=2)
        nbrs = neigh.fit(pd_features_scaled)
        distances, indices = nbrs.kneighbors(pd_features_scaled)
        sorted_distances = np.sort(distances, axis=0)
        sorted_distances = sorted_distances[:, 1]

        i = np.arange(len(sorted_distances))
        knee = KneeLocator(i, sorted_distances, S=1, curve='convex', direction='increasing', interp_method='polynomial')

        if knee.knee:
            epsilon = sorted_distances[knee.knee]
        else:
            epsilon = sorted_distances[round(len(sorted_distances) / 2)]

        if IS_CUSTOMIZED_EPSILON and epsilon < EPSILON_THRESHOLD:
            epsilon = EPSILON_THRESHOLD

        if epsilon != 0:
            # Cluster the features based on eps
            db_clusters = DBSCAN(eps=epsilon, min_samples=1, metric='euclidean').fit_predict(pd_features_scaled)
        else:
            db_clusters = [0 for i in range(len(pd_features))]
        num_clusters = len(set(db_clusters))
        all_vio = len(pd_features_scaled)
        unique_vio = num_clusters
        elim_ratio = 100 * (1 - float(num_clusters) / len(pd_features_scaled))
        return db_clusters, all_vio, unique_vio, elim_ratio

    def analyze_vio(self, db_clusters, epsilon, distances):
        cluster_id = db_clusters[-1]
        if cluster_id not in db_clusters[:-1]:
            check_similar = False
        else:
            check_similar = True
        print(f"epsilon: {epsilon} vs. distance: {distances[-1][-1]} -> Emerged: {not check_similar}")


if __name__ == "__main__":
    group_name_list = ["all(iter1)", "all(iter2)", "all(iter3)"]

    target_name_list = ["scenoRITA_borregas_ave_GA", "scenoRITA_borregas_ave_T-way", "scenoRITA_borregas_ave_ConfVD",
                        "scenoRITA_san_mateo_GA", "scenoRITA_san_mateo_T-way", "scenoRITA_san_mateo_ConfVD",
                        "scenoRITA_sunnyvale_loop_GA", "scenoRITA_sunnyvale_loop_T-way", "scenoRITA_sunnyvale_loop_ConfVD",
                        "DoppelTest_borregas_ave_GA", "DoppelTest_borregas_ave_T-way", "DoppelTest_borregas_ave_ConfVD",
                        "DoppelTest_san_mateo_GA", "DoppelTest_san_mateo_T-way", "DoppelTest_san_mateo_ConfVD",
                        "DoppelTest_sunnyvale_loop_GA", "DoppelTest_sunnyvale_loop_T-way", "DoppelTest_sunnyvale_loop_ConfVD",
                        "ADFuzz_borregas_ave_GA", "ADFuzz_borregas_ave_T-way", "ADFuzz_borregas_ave_ConfVD",
                        "AVFuzzer_San_Francisco_GA", "AVFuzzer_San_Francisco_T-way", "AVFuzzer_San_Francisco_ConfVD"]
    # target_name_list = ["scenoRITA_borregas_ave_GA", "scenoRITA_borregas_ave_ConfVD",
    #                     "scenoRITA_san_mateo_GA", "scenoRITA_san_mateo_ConfVD",
    #                     "scenoRITA_sunnyvale_loop_GA", "scenoRITA_sunnyvale_loop_ConfVD",
    #                     "DoppelTest_borregas_ave_GA", "DoppelTest_borregas_ave_ConfVD",
    #                     "DoppelTest_san_mateo_GA", "DoppelTest_san_mateo_ConfVD",
    #                     "DoppelTest_sunnyvale_loop_GA", "DoppelTest_sunnyvale_loop_ConfVD",
    #                     "ADFuzz_borregas_ave_GA", "ADFuzz_borregas_ave_ConfVD",
    #                     "AVFuzzer_San_Francisco_GA", "AVFuzzer_San_Francisco_ConfVD"]

    approach_list = ["scenoRITA", "DoppelTest", "ADFuzz", "AVFuzzer"]

    oracle_list = ["CollisionOracle.csv", "AccelOracle.csv", "DecelOracle.csv", "SpeedingOracle.csv",
                   "UnsafeLaneChangeOracle.csv", "JunctionLaneChangeOracle.csv",
                   "ModuleDelayOracle.csv", "PlanningFailure.csv", "PlanningGeneratesGarbage.csv"]

    map_list = ["borregas_ave", "san_mateo", "sunnyvale_loop", "San_Francisco"]

    # output_oracle_list = ["Collision", "Fast Acceleration", "Hard Braking", "Speeding", "Unsafe Lane-change",
    #                       "Module Delay", "Module Malfunction", "Vehicle Paralysis", "Lane-change in Junction",
    #                       "Total"]

    output_oracle_list = ["Collision", "Fast Accel.", "Hard Brak.", "Speeding", "Unsafe LC", "LC in Junc.",
                          "Delay", "Malfunc.", "Paraly.",
                          "Total"]

    df_unique_final = pd.DataFrame()
    df_all_final = pd.DataFrame()

    for group_name in group_name_list:
        df_unique_dict = {}
        df_all_dict = {}
        for target_name in target_name_list:
            print("-----------------------------------")
            print(target_name)

            target_dir = f"{FEATURES_CSV_DIR}/{group_name}/{target_name}/violation_features"
            csv_files_name_list = [name for name in os.listdir(target_dir) if ".csv" in name]

            output_dir = f"{target_dir}/output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            print("ViolationType,  Violations No.,  Violations No.(Unique),  Elimination%")

            eliminator = Eliminator()
            oracle_unique_list = []
            oracle_all_list = []

            for oracle in oracle_list:
                oracle_type = oracle.split(".")[0]

                if oracle in csv_files_name_list:
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
                        try:
                            output_file_path = f"{output_dir}/clustered_{oracle}"
                            pd_features = pd_data.iloc[:, 1:]
                            db_clusters, all_vio, unique_vio, elim_ratio = eliminator.cluster(pd_features)
                            pd_data.insert(0, "clusters", db_clusters, True)
                            message = oracle_type + ',  {:,},  {:,},  {:.2f}%'
                            print(message.format(all_vio, unique_vio, elim_ratio))
                            pd_data.to_csv(output_file_path, index=False)
                        except:
                            unique_vio = len(pd_data)
                            all_vio = unique_vio
                            print(f"Cannot eliminate {oracle_type}")

                    oracle_unique_list.append(unique_vio)
                    oracle_all_list.append(all_vio)
                else:
                    oracle_unique_list.append(0)
                    oracle_all_list.append(0)
            oracle_unique_list.append(sum(oracle_unique_list))
            oracle_all_list.append(sum(oracle_all_list))
            df_unique_dict[target_name] = oracle_unique_list
            df_all_dict[target_name] = oracle_all_list

        if not df_unique_final.empty:
            df_unique_final += pd.DataFrame(data=df_unique_dict)
        else:
            df_unique_final = pd.DataFrame(data=df_unique_dict)
        if not df_all_final.empty:
            df_all_final += pd.DataFrame(data=df_all_dict)
        else:
            df_all_final = pd.DataFrame(data=df_all_dict)

    df_unique_final = round(df_unique_final / len(group_name_list))
    df_all_final = round(df_all_final / len(group_name_list))

    df_unique_final = df_unique_final.astype(int)
    df_all_final = df_all_final.astype(int)

    df_unique_final.iloc[-1] = df_unique_final.iloc[0:-1].sum()
    df_all_final.iloc[-1] = df_all_final.iloc[0:-1].sum()

    latex_generator = LatexGenerator(df_unique_final, df_all_final, approach_list, map_list, output_oracle_list)
    latex_generator.start_write()
