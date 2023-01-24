import os
import numpy as np
import pandas as pd
from kneed import KneeLocator
# from matplotlib import pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from config import FEATURES_CSV_DIR


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

        message = csv_file_name + ',  {:,},  {:,},  {:.2f}%'
        print(message.format(len(pd_features_scaled), num_clusters,
                             100 * (1 - float(num_clusters) / len(pd_features_scaled))))

        pd_data.insert(0, "clusters", db_clusters, True)
        return pd_data


if __name__ == "__main__":
    target_approach = "DoppelTest"  # scenoRITA
    target_name = "borregas_ave_30s"  # borregas_ave_30s/sunnyvale_loop_10s

    target_dir = f"{FEATURES_CSV_DIR}/{target_approach}/{target_name}"
    csv_files_name_list = [name for name in os.listdir(target_dir) if ".csv" in name]

    output_dir = f"{FEATURES_CSV_DIR}/{target_approach}/{target_name}/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("ViolationType,  Violations No.,  Violations No.(Unique),  Elimination%")

    eliminator = Eliminator()

    for csv_file_name in csv_files_name_list:
        csv_file_path = os.path.join(target_dir, csv_file_name)
        pd_data = pd.read_csv(csv_file_path, encoding='utf-8')
        if len(pd_data) > 5:
            output_file_path = f"{output_dir}/clustered_{csv_file_name}"
            output_data = eliminator.cluster(pd_data, csv_file_name)
            output_data.to_csv(output_file_path, index=False)
