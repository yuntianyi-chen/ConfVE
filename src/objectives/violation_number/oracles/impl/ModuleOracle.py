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
        self.distance_traveled = -1.0
        self.received_routing = False
        self.received_planning = False
        self.received_prediction = False

    def get_interested_topics(self):
        return [
            '/apollo/routing_response',
            '/apollo/planning',
            '/apollo/prediction'
        ]

    def on_new_message(self, topic: str, message, t):
        if topic == '/apollo/routing_response':
            self.received_routing = True
        if topic == '/apollo/planning':
            self.received_planning = True
        if topic == '/apollo/prediction':
            self.received_prediction = True

    def get_result(self):
        result = list()
        if not self.received_routing:
            result.append(('module', 'routing failure'))
        if not self.received_planning:
            result.append(('module', 'planning failure'))
        if not self.received_prediction:
            result.append(('module', 'prediction failure'))
        # elif self.distance_traveled == -1.0:
        #     result.append(('module', 'sim control failure'))
        return result