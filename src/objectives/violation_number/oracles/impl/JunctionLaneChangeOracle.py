from typing import List
from shapely.geometry import Polygon, Point
from objectives.violation_number.oracles.OracleInterface import OracleInterface
from objectives.violation_number.oracles.Violation import Violation
from tools.hdmap.MapParser import MapParser


class JunctionLaneChangeOracle(OracleInterface):
    """
    Junction Lane Change Oracle is responsible for checking if the ADS makes a lane-change decision while inside a
    junction.
        * x:            float
        * y:            float
        * heading:      float
        * speed:        float
        * junction_id:  int     # index of junction_id in a sorted list
    """

    def __init__(self) -> None:
        super().__init__()
        self.mp = MapParser.get_instance()
        self.junctions = list()
        for j_id in self.mp.get_junctions():
            j_obj = self.mp.get_junction_by_id(j_id)
            junction_polygon = Polygon([[x.x, x.y] for x in j_obj.polygon.point])
            self.junctions.append(
                (j_id, junction_polygon)
            )
        self.junction_ids = sorted(self.mp.get_junctions())
        self.last_localization = None
        self.violation = list()

    def get_interested_topics(self) -> List[str]:
        return [
            '/apollo/planning',
            '/apollo/localization/pose'
        ]

    def current_junction(self):
        if self.last_localization is None:
            return ''
        p = self.last_localization.pose.position
        ego_position = Point(p.x, p.y)

        for j_id, j_poly in self.junctions:
            if ego_position.within(j_poly):
                return j_id
        return ''

    def on_planning(self, message):
        if self.last_localization is None:
            return
        main_decision = message.decision.main_decision
        change_lane_type = None
        if main_decision.HasField('cruise'):
            change_lane_type = main_decision.cruise.change_lane_type
        elif main_decision.HasField('stop'):
            change_lane_type = main_decision.stop.change_lane_type
        # modules/routing/proto/routing.proto#70
        changing_lane = change_lane_type is not None and change_lane_type in [
            1, 2]
        junction_id = self.current_junction()
        if changing_lane and junction_id != '':
            features = self.get_basic_info_from_localization(self.last_localization)
            features['junction_id'] = self.junction_ids.index(junction_id)
            self.violation.append(Violation(
                'JunctionLaneChangeOracle',
                features,
                str(features['junction_id'])
            ))

    def on_localization(self, message):
        self.last_localization = message

    def on_new_message(self, topic: str, message, t):
        if len(self.violation) > 0:
            # violation already tracked
            return
        if topic == '/apollo/planning':
            self.on_planning(message)
        else:
            self.on_localization(message)

    def get_result(self):
        return self.violation
