from typing import Optional
from objectives.violation_number.oracles.OracleInterface import OracleInterface
from modules.localization.proto.localization_pb2 import LocalizationEstimate
from shapely.geometry import Point

from objectives.violation_number.oracles.Violation import Violation


class ModuleOracle(OracleInterface):
    """
    Module Oracle is responsible for checking and categorizing module failures
    Its features include:
        * x: float
        * y: float
        * heading: float
        * speed: float
        * type: int

    :todo: update the names
    Error code for type includes:
        * 400: Routing Failure
        * 401: Prediction Failure
        * 402: Planning Failure

        * 500: Car never moved
        * 501: Planning generates garbage
    """
    distance_traveled: float

    def __init__(self) -> None:
        self.prev_ = None
        self.next_ = None
        self.last_localization = None

        self.received_routing = False
        self.received_planning = False
        self.received_prediction = False

        self.has_normal_planning_decision = False
        self.distance_traveled = 0

    def get_interested_topics(self):
        return [
            '/apollo/routing_response',
            '/apollo/planning',
            '/apollo/prediction',
            '/apollo/localization/pose'
        ]

    def on_new_message(self, topic: str, message, t):
        if topic == '/apollo/routing_response':
            self.received_routing = True
        if topic == '/apollo/prediction':
            self.received_prediction = True
        if topic == '/apollo/planning':
            self.received_planning = True
            if not self.has_normal_planning_decision:
                self.last_planning = message
                if self.is_adc_planner_making_normal_decision():
                    self.has_normal_planning_decision = True

        # if self.distance_traveled <= 0:
        if topic == '/apollo/localization/pose':
            self.last_localization = message
            if self.prev_ is None and self.next_ is None:
                self.prev_ = message
                return
            self.next_ = message
            prev_point = Point(self.prev_.pose.position.x, self.prev_.pose.position.y, self.prev_.pose.position.z)
            next_point = Point(self.next_.pose.position.x, self.next_.pose.position.y, self.next_.pose.position.z)
            self.distance_traveled = prev_point.distance(next_point)
            # self.prev_ = message

    def is_adc_planner_making_normal_decision(self):
        planning_main_decision = self.last_planning.decision.main_decision
        if str(planning_main_decision).strip() == "":
            return False
        if str(planning_main_decision.not_ready).strip() != "":
            return False
        return True

    def get_result(self):
        result = list()
        feature = self.get_basic_info_from_localization(self.last_localization)
        if not self.received_routing:
            # result.append(('module', 'Routing fails to start'))
            vf = dict(feature)
            vf['type'] = 400
            result.append(Violation(
                'ModuleOracle', vf
            ))
        if not self.received_prediction:
            # result.append(('module', 'Prediction fails to start'))
            vf = dict(feature)
            vf['type'] = 401
            result.append(Violation(
                'ModuleOracle', vf
            ))
        if not self.received_planning:
            # result.append(('module', 'Planning fails to start'))
            vf = dict(feature)
            vf['type'] = 402
            result.append(Violation(
                'ModuleOracle', vf
            ))

        if self.received_planning and self.received_routing and self.received_prediction:
            if self.distance_traveled == 0:
                if self.has_normal_planning_decision:
                    # result.append(('module', 'Running car stops indefinitely'))
                    vf = dict(feature)
                    vf['type'] = 500
                    result.append(Violation(
                        'ModuleOracle', vf
                    ))
                else:
                    # result.append(('module', 'Planning generates garbage'))
                    vf = dict(feature)
                    vf['type'] = 501
                    result.append(Violation(
                        'ModuleOracle', vf
                    ))
        return result
