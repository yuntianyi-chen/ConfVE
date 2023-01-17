from typing import Optional
from objectives.violation_number.oracles.OracleInterface import OracleInterface
from modules.localization.proto.localization_pb2 import LocalizationEstimate
from shapely.geometry import Point


class ModuleOracle(OracleInterface):
    prev_: Optional[LocalizationEstimate]
    next_: Optional[LocalizationEstimate]

    distance_traveled: float

    def __init__(self) -> None:
        self.prev_ = None
        self.next_ = None

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
        if not self.received_routing:
            result.append(('module', 'routing failure'))
        if not self.received_planning:
            result.append(('module', 'planning failure'))
        if not self.received_prediction:
            result.append(('module', 'prediction failure'))

        if self.received_planning and self.received_routing and self.received_prediction:
            if self.distance_traveled == 0:
                if self.has_normal_planning_decision:
                    result.append(('module', 'other crash: has planning decision but not moving'))
                else:
                    result.append(('module', 'planning crash: no planning decision and not moving'))
        return result
