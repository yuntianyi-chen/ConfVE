from typing import List, Optional, Tuple
from objectives.violation_number.oracles.OracleInterface import OracleInterface
from modules.localization.proto.localization_pb2 import LocalizationEstimate
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles
from shapely.geometry import Polygon, LineString
from objectives.violation_number.oracles.Violation import Violation
from tools.utils import generate_adc_polygon, calculate_velocity


def is_adc_responsible(front_edge: LineString, obs_polygon: Polygon) -> bool:
    return front_edge.distance(obs_polygon) == 0.0


class CollisionOracle(OracleInterface):
    """
    Collision Oracle is responsible for checking whether collision occurred between the ego vehicle and another
    road traffic participants.
    Its features include:
        x:              float
        y:              float
        heading:        float
        speed:          float
        obs_id:         int
        obs_x:          float
        obs_y:          float
        obs_heading:    float
        obs_speed:      float
        obs_type:       int
    """
    last_localization: Optional[LocalizationEstimate]
    last_perception: Optional[PerceptionObstacles]
    distances: List[Tuple[float, int, str]]

    def __init__(self) -> None:
        self.last_localization = None
        self.last_perception = None
        self.excluded_obs = set()
        self.violations = list()

    def get_interested_topics(self):
        return [
            '/apollo/localization/pose',
            '/apollo/perception/obstacles'
        ]

    def on_new_message(self, topic: str, message, t):
        if topic == '/apollo/localization/pose':
            self.last_localization = message
        else:
            self.last_perception = message

        if self.last_localization is None or self.last_perception is None:
            # cannot analyze
            return

        # begin analyze
        adc_pose = self.last_localization.pose

        adc_polygon_pts = generate_adc_polygon(adc_pose.position, adc_pose.heading)

        adc_front_line_string = LineString(
            [[x.x, x.y] for x in (adc_polygon_pts[0], adc_polygon_pts[3])])

        adc_polygon = Polygon([[x.x, x.y] for x in adc_polygon_pts])

        for obs in self.last_perception.perception_obstacle:
            obs_id = obs.id
            if obs_id in self.excluded_obs:
                # obstacle may pass through ego vehicle if they are not smart
                continue
            obs_polygon = Polygon([[x.x, x.y] for x in obs.polygon_point])
            if adc_polygon.distance(obs_polygon) == 0:
                self.excluded_obs.add(obs_id)

                if not is_adc_responsible(adc_front_line_string, obs_polygon):
                    continue
                # collision occurred
                features = self.get_basic_info_from_localization(self.last_localization)
                features['obs_id'] = obs.id
                features['obs_x'] = obs.position.x
                features['obs_y'] = obs.position.y
                features['obs_heading'] = obs.theta
                features['obs_speed'] = calculate_velocity(obs.velocity)
                features['obs_type'] = obs.type

                self.violations.append(
                    Violation(
                        'CollisionOracle',
                        features,
                        str(features['obs_id'])
                    )
                )

    def is_adc_completely_stopped(self) -> bool:
        adc_pose = self.last_localization.pose
        adc_velocity = calculate_velocity(adc_pose.linear_velocity)
        return adc_velocity == 0

    def get_result(self):
        return self.violations
