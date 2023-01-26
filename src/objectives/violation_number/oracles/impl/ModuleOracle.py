from shapely.geometry import Point
from objectives.violation_number.oracles.OracleInterface import OracleInterface
from objectives.violation_number.oracles.Violation import Violation


class ModuleOracle(OracleInterface):
    """
    Module Oracle is responsible for checking and categorizing module failures
    Its features include:
        # * x: float
        # * y: float
        # * heading: float
        # * speed: float
        # * type: int

    :todo: update the names
    Error code for type includes:
        * 400: Routing Failure
        * 401: Prediction Failure
        * 402: Planning Failure

        * 500: Car never moved
        * 501: Planning generates garbage

        * 600: SimControlFailure
    """
    distance_traveled: float

    def __init__(self) -> None:
        self.prev_ = None
        self.next_ = None
        self.last_localization = None

        self.received_routing = False
        self.received_planning = False
        self.received_prediction = False
        self.received_localization = False

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
        if topic == '/apollo/localization/pose':
            self.received_localization = True
            self.last_localization = message
            if self.prev_ is None and self.next_ is None:
                self.prev_ = message
                return
            self.next_ = message
            prev_point = Point(self.prev_.pose.position.x, self.prev_.pose.position.y, self.prev_.pose.position.z)
            next_point = Point(self.next_.pose.position.x, self.next_.pose.position.y, self.next_.pose.position.z)
            self.distance_traveled = prev_point.distance(next_point)

    def is_adc_planner_making_normal_decision(self):
        planning_main_decision = self.last_planning.decision.main_decision
        if str(planning_main_decision).strip() == "":
            return False
        if str(planning_main_decision.not_ready).strip() != "":
            return False
        return True

    def get_result(self):
        result = list()
        if self.received_localization:
            feature = self.get_basic_info_from_localization(self.last_localization)
            if not self.received_routing:
                vf = dict(feature)
                vf['type'] = 400
                result.append(Violation(
                    'RoutingFailure', vf, str(vf['type'])
                ))
            if not self.received_prediction:
                vf = dict(feature)
                vf['type'] = 401
                result.append(Violation(
                    'PredictionFailure', vf, str(vf['type'])
                ))
            if not self.received_planning:
                vf = dict(feature)
                vf['type'] = 402
                result.append(Violation(
                    'PlanningFailure', vf, str(vf['type'])
                ))

            if self.received_planning and self.received_routing and self.received_prediction:
                if self.distance_traveled == 0:
                    if self.has_normal_planning_decision:
                        vf = dict(feature)
                        vf['type'] = 500
                        result.append(Violation(
                            'CarNeverMoved', vf, str(vf['type'])
                        ))
                    else:
                        vf = dict(feature)
                        vf['type'] = 501
                        result.append(Violation(
                            'PlanningGeneratesGarbage', vf, str(vf['type'])
                        ))
        else:
            if self.received_planning and self.received_routing and self.received_prediction:
                vf = dict()
                vf['type'] = 600
                result.append(Violation(
                    'LocalizationFailure', vf, str(vf['type'])
                ))
        return result
