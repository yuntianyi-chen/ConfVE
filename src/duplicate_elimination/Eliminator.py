import numpy as np
from kneed import KneeLocator
from matplotlib import pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

# warnings.simplefilter('ignore', np.RankWarning)

class Eliminator:

    def __init__(self):
      return


    def classifier(self):
        return

    def cluster(self, data_scaled, selectedData, message, data, vfile):
        # Automtically determine the value of epsilon
        neigh = NearestNeighbors(n_neighbors=2)
        nbrs = neigh.fit(selectedData)
        distances, indices = nbrs.kneighbors(selectedData)
        distances = np.sort(distances, axis=0)
        distances = distances[:, 1]

        # plt.plot(distances)
        # plt.show()

        i = np.arange(len(distances))
        knee = KneeLocator(i, distances, S=1, curve='convex', direction='increasing', interp_method='polynomial')
        # knee.plot_knee()
        # plt.show()
        if knee.knee:
            epsilon = distances[knee.knee]
        else:
            epsilon = distances[round(len(distances)/2)-1]
        # Cluster the features based on eps
        db_clusters = DBSCAN(eps=epsilon, min_samples=1, metric='cityblock').fit_predict(data_scaled)
        num_clusters = len(set(db_clusters))
        print(message.format(len(data_scaled), num_clusters, 100 * (1 - float(num_clusters) / len(data_scaled))))

        # store cluster values
        data.insert(0, "clusters", db_clusters, True)
        data.to_csv(vfile, index=False)

    def collision(self, data):
        # COLLISION
        message = 'Collision,{:,},{:,},{:.2f}%'
        # filter out non-collision violations
        a_series = (data[["c_x", "c_y"]] != 0).any(axis=1)
        features = data.loc[a_series]
        features = features[
            ["record_name", "c_x", "c_y", "c_type", "adc_heading", "adc_speed", "obs_heading", "obs_speed", "obs_type",
             "obs_len", "obs_wid", "obs_height"]]
        # scale the features, so all of them are on the same magnitude
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(features[["c_x", "c_y", "c_type", "adc_heading", "adc_speed", "obs_heading",
                                                     "obs_speed", "obs_type", "obs_len", "obs_wid", "obs_height"]])
        selected_features = scaler.fit_transform(features[["c_x", "c_y", "c_type", "obs_type"]])
        self.cluster(data_scaled, selected_features, message, features, "DBSCAN_c.csv")

    def speeding(self, data):
        # SPEED
        message = 'Speeding,{:,},{:,},{:.2f}%'
        # filter out non-speed violations
        a_series = (data[["speeding_x", "speeding_y"]] != 0).any(axis=1)
        features = data.loc[a_series]
        if len(features) >= 3:
            features = features[
                ["record_name", "speeding_x", "speeding_y", "speeding_value", "speeding_duration", "speeding_heading"]]
            # scale the features, so all of them are on the same magnitude
            scaler = MinMaxScaler()
            data_scaled = scaler.fit_transform(
                features[["speeding_x", "speeding_y", "speeding_value", "speeding_duration", "speeding_heading"]])
            self.cluster(data_scaled, data_scaled, message, features, "DBSCAN_s.csv")
        else:
            print(message.format(0, 0, 0, 0))

    def unsafe_lane_change(self, data):
        # USLC
        message = 'UnsafeLaneChange,{:,},{:,},{:.2f}%'
        # filter out non-uslc violations
        a_series = (data[["uslc_x", "uslc_y"]] != 0).any(axis=1)
        features = data.loc[a_series]
        features = features[["record_name", "uslc_x", "uslc_y", "uslc_duration", "uslc_heading"]]
        # scale the features, so all of them are on the same magnitude
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(features[["uslc_x", "uslc_y", "uslc_duration", "uslc_heading"]])
        selected_features = scaler.fit_transform(features[["uslc_x", "uslc_y", "uslc_heading"]])
        self.cluster(data_scaled, selected_features, message, features, "DBSCAN_uslc.csv")

    def accel(self, data):
        # FA
        message = 'FastAccel,{:,},{:,},{:.2f}%'
        # filter out non-fa violations
        a_series = (data[["fastAccl_x", "fastAccl_y"]] != 0).any(axis=1)
        features = data.loc[a_series]
        features = features[
            ["record_name", "fastAccl_x", "fastAccl_y", "fastAccl_duration", "fastAccl_value", "fastAccl_heading"]]
        # scale the features, so all of them are on the same magnitude
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(
            features[["fastAccl_x", "fastAccl_y", "fastAccl_duration", "fastAccl_value", "fastAccl_heading"]])
        selected_features = scaler.fit_transform(features[["fastAccl_x", "fastAccl_y"]])
        self.cluster(data_scaled, selected_features, message, features, "DBSCAN_fa.csv")

    def hardbrake(self, data):
        # HB
        message = 'HardBrake,{:,},{:,},{:.2f}%'
        # filter out non-hb violations
        a_series = (data[["hardBrake_x", "hardBrake_y"]] != 0).any(axis=1)
        features = data.loc[a_series]
        features = features[
            ["record_name", "hardBrake_x", "hardBrake_y", "hardBrake_value", "hardBrake_duration", "hardBrake_heading"]]
        # scale the features, so all of them are on the same magnitude
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(
            features[["hardBrake_x", "hardBrake_y", "hardBrake_value", "hardBrake_duration", "hardBrake_heading"]])
        selected_features = scaler.fit_transform(features[["hardBrake_x", "hardBrake_y"]])
        self.cluster(data_scaled, selected_features, message, features, "DBSCAN_hb.csv")

