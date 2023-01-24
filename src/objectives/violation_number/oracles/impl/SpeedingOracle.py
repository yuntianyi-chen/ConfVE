from datetime import datetime
from itertools import groupby
from typing import List
from objectives.violation_number.oracles.OracleInterface import OracleInterface
from objectives.violation_number.oracles.Violation import Violation
from tools.hdmap.MapParser import MapParser
from shapely.geometry import Point
from tools.utils import calculate_velocity


class SpeedingOracle(OracleInterface):
    """
    Speeding Oracle is responsible for checking if the ego vehicle violates speed limit at any point
    Its features include:
        * x:            float
        * y:            float
        * heading:      float
        * speed:        float
        * speed_limit:  float
        * duration:     float
    """

    TOLERANCE = 0.025

    def __init__(self) -> None:
        self.mp = MapParser.get_instance()
        self.lanes = dict()

        self.min_speed_limit = None

        for lane in self.mp.get_lanes():
            lane_obj = self.mp.get_lane_by_id(lane)
            speed_limit = lane_obj.speed_limit
            central_curve = self.mp.get_lane_central_curve(lane)
            self.lanes[lane] = (speed_limit, central_curve)

            if self.min_speed_limit is None or speed_limit < self.min_speed_limit:
                self.min_speed_limit = speed_limit
        
        self.cached_lanes = set()
        self.trace = list()

    def get_interested_topics(self) -> List[str]:
        return ['/apollo/localization/pose']

    def on_new_message(self, topic: str, message, t):
        p = message.pose.position
        ego_position = Point(p.x, p.y, p.z)
        ego_velocity = calculate_velocity(message.pose.linear_velocity)

        if ego_velocity <= self.min_speed_limit * (1 + SpeedingOracle.TOLERANCE):
            # cannot violate any speed limit
            self.trace.append((False, t, -1, dict()))
            return

        for lane_id in self.cached_lanes:
            lane_speed_limit, lane_curve = self.lanes[lane_id]
            ego_position.distance(lane_curve)
            if ego_position.distance(lane_curve) <= 1:
                if ego_velocity > lane_speed_limit * (1 + SpeedingOracle.TOLERANCE):
                    features = self.get_basic_info_from_localization(message)
                    features['speed_limit'] = lane_speed_limit
                    self.trace.append((True, t, lane_speed_limit, features))
                    return
                self.trace.append((False, t, -1, dict()))
                return

        for lane_id in self.lanes:
            lane_speed_limit, lane_curve = self.lanes[lane_id]
            if round(ego_position.distance(lane_curve), 1) <= 1:
                self.update_cached_lanes(lane_id)
                if ego_velocity > lane_speed_limit * (1 + SpeedingOracle.TOLERANCE):
                    features = self.get_basic_info_from_localization(message)
                    features['speed_limit'] = lane_speed_limit
                    self.trace.append((True, t, lane_speed_limit, features))
                    return
                self.trace.append((False, t, -1, dict()))
                return

        self.trace.append((False, t, -1, dict()))

    def update_cached_lanes(self, lane_id:str):
        self.cached_lanes.add(lane_id)

    def get_result(self):
        violations = list()
        for k, v in groupby(self.trace, key=lambda x: (x[0], x[2])):
            traces = list(v)
            start_time = datetime.fromtimestamp(traces[0][1] / 1000000000)
            end_time = datetime.fromtimestamp(traces[-1][1] / 1000000000)
            delta_t = (end_time - start_time).total_seconds()

            if k[0]:
                features = dict(traces[0][3])
                features['duration'] = delta_t
                violations.append(Violation(
                    'SpeedingOracle',
                    features,
                    str(features['speed'])
                ))

        return violations
