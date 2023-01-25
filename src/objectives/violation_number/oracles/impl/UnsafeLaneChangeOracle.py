from typing import List
from datetime import datetime
from itertools import groupby
from shapely.geometry import Polygon
from tools.hdmap.MapParser import MapParser
from objectives.violation_number.oracles.Violation import Violation
from objectives.violation_number.oracles.OracleInterface import OracleInterface
from tools.utils import generate_adc_polygon, construct_lane_boundary_linestring


class UnsafeLaneChangeOracle(OracleInterface):
    """
    Unsafe Lane Change Oracle is responsible for checking if the vehicle spends a higher than usual
    amount of time on the lane boundaries, which is unsafe.
        * x:            float
        * y:            float
        * heading:      float
        * speed:        float
        * boundary_id:  int     # index of the boundary ID in a sorted list
        * duration:     float
    """
    ADC_INTERSECTING_LANE_BOUNDARY_MAX_LOOK_BACK_FRAMES_IN_SECOND = 5.0
    PRUNE_DISTANCE = 150

    def __init__(self) -> None:
        self.mp = MapParser.get_instance()
        self.boundaries = dict()
        self.get_boundaries()
        self.boundary_ids = sorted(self.boundaries.keys())
        self.__data = list()  # [ (intersects?, timestamp, boundary_id, feature) ]

        self.searchable_boundary_ids = set(self.boundary_ids)

    def get_boundaries(self):
        for lane_id in self.mp.get_lanes():
            lane = self.mp.get_lane_by_id(lane_id)
            lboundary, rboundary = construct_lane_boundary_linestring(lane)
            self.boundaries[f"{lane_id}_L"] = lboundary
            self.boundaries[f"{lane_id}_R"] = rboundary
    
    def on_new_message(self, topic: str, message, t):
        ego_pts = generate_adc_polygon(message.pose.position, message.pose.heading)
        ego_polygon = Polygon([[x.x, x.y] for x in ego_pts])
        pending_removal_boundary_ids = set()
        for bid in self.searchable_boundary_ids:
            distance = ego_polygon.distance(self.boundaries[bid])
            if distance == 0:
                # intersection found
                features = self.get_basic_info_from_localization(message)
                features['boundary_id'] = self.boundary_ids.index(bid)
                if features["speed"] > 0:
                    self.__data.append((True, t, bid, features))
                else:
                    self.__data.append((False, t, '', {}))
                return
            if distance > UnsafeLaneChangeOracle.PRUNE_DISTANCE:
                pending_removal_boundary_ids.add(bid)
        
        self.searchable_boundary_ids = self.searchable_boundary_ids - pending_removal_boundary_ids

        # no intersection
        self.__data.append((False, t, '', {}))
        
    def get_interested_topics(self) -> List[str]:
        return ["/apollo/localization/pose"]
    
    def get_result(self):
        violations = list()
        for k, v in groupby(self.__data, key=lambda x: (x[0], x[2])):
            intersects, b_id = k
            traces = list(v)
            if intersects and len(traces) > 1:
                start_time = datetime.fromtimestamp(traces[0][1]/1000000000)
                end_time = datetime.fromtimestamp(traces[-1][1]/1000000000)
                delta_t = (end_time - start_time).total_seconds()

                if delta_t > self.ADC_INTERSECTING_LANE_BOUNDARY_MAX_LOOK_BACK_FRAMES_IN_SECOND:
                    features = dict(traces[0][3])
                    features['duration'] = delta_t
                    violations.append(
                        Violation(
                            'UnsafeLaneChangeOracle',
                            features,
                            str(features['boundary_id'])
                        )
                    )
        return violations
