import math
from datetime import datetime
from itertools import groupby
from typing import List, Optional
from objectives.violation_number.oracles.OracleInterface import OracleInterface
from modules.localization.proto.localization_pb2 import LocalizationEstimate
from objectives.violation_number.oracles.Violation import Violation
from tools.utils import calculate_velocity


class ComfortOracle(OracleInterface):
    """
    Comfort Oracle is responsible for checking whether fast acceleration or hard braking occurred during a scenario
    Its features include:
        * x:            float
        * y:            float
        * heading:      float
        * speed:        float
        * accel:        float
        * duration:     float
        * type:         float (1.0 => fast acceleration, -1.0 => hard braking)
    """
    prev_: Optional[LocalizationEstimate]
    next_: Optional[LocalizationEstimate]
    accl: List[float]
    violations: List[Violation]

    MAX_ACCL = 4.0
    MAX_DCCL = -4.0
    TOLERANCE = 0.025

    def __init__(self) -> None:
        self.prev_ = None
        self.next_ = None
        self.trace = list()

    def get_interested_topics(self):
        return ['/apollo/localization/pose']

    def get_accel_value(self) -> float:
        accel_x = self.next_.pose.linear_acceleration.x
        accel_y = self.next_.pose.linear_acceleration.y
        accel_z = self.next_.pose.linear_acceleration.z

        accel_value = math.sqrt(accel_x ** 2 + accel_y ** 2 + accel_z ** 2)
        return accel_value

    def on_new_message(self, topic: str, message, t):
        if self.prev_ is None and self.next_ is None:
            self.prev_ = message
            return
        self.next_ = message

        # compare velocity
        accel_value = self.get_accel_value()

        prev_velocity = calculate_velocity(self.prev_.pose.linear_velocity)
        next_velocity = calculate_velocity(self.next_.pose.linear_velocity)
        direction = next_velocity - prev_velocity

        if direction < 0:
            accel = accel_value * -1
        else:
            accel = accel_value

        features = self.get_basic_info_from_localization(self.next_)
        features['accel'] = accel

        if accel > ComfortOracle.MAX_ACCL * (1 + ComfortOracle.TOLERANCE):
            self.trace.append((1, t, features))
        elif accel < ComfortOracle.MAX_DCCL * (1 + ComfortOracle.TOLERANCE):
            self.trace.append((-1, t, features))
        else:
            self.trace.append((0, t, None))

        self.prev_ = message

    def get_result(self):
        violations = list()
        for k, v in groupby(self.trace, key=lambda x: x[0]):
            traces = list(v)
            start_time = datetime.fromtimestamp(traces[0][1] / 1000000000)
            end_time = datetime.fromtimestamp(traces[-1][1] / 1000000000)
            delta_t = (end_time - start_time).total_seconds()
            if k == 1:
                features = dict(traces[0][2])
                features['duration'] = delta_t
                features['type'] = 1.0
                violations.append(Violation(
                    'AccelOracle',
                    features,
                    str(features['accel'])
                ))
            elif k == -1:
                features = dict(traces[0][2])
                features['duration'] = delta_t
                features['type'] = -1.0
                violations.append(Violation(
                    'DecelOracle',
                    features,
                    str(features['accel'])
                ))

        return violations
