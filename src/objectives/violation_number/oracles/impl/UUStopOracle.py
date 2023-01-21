from typing import List, Tuple, Optional
from objectives.violation_number.oracles.OracleInterface import OracleInterface
from modules.localization.proto.localization_pb2 import LocalizationEstimate
from modules.planning.proto.decision_pb2 import STOP_REASON_STOP_SIGN
from modules.planning.proto.planning_pb2 import ADCTrajectory
from objectives.violation_number.oracles.Violation import Violation
from tools.hdmap.MapParser import MapParser
from tools.utils import calculate_velocity


class UUStopOracle(OracleInterface):
    """
    Unusual Stop Oracle is responsible for checking if the ADS makes a stop decision for stop sign and stops there
    for more than 10 seconds. In a normal scenario, once ADS stops for a stop sign, it should enter a stop sign
    scenario, remove that stop sign, and proceed when the road is clear. Therefore stopping for more than 10 seconds
    for stop sign is unusual, it is, however, possible that the ADS stops for other reasons.
    Its features include:
        * x:            float
        * y:            float
        * heading:      float
        * speed:        float
        * reason_code:  int     # stop reason code modules/planning/proto/decision.proto StopReasonCode
    """

    last_localization = Optional[LocalizationEstimate]
    last_planning = Optional[ADCTrajectory]

    first_stop_timestamp: float
    violated_stop_sign_stopped_times: List[Tuple[float, str]]

    # STOP_SIGN_VO_ID_PREFIX = "SS_"
    ADC_MAX_STOP_TIME_ON_STOP_SIGN_IN_SECOND = 10.0

    # MAX_ABS_SPEED_WHEN_STOPPED = 0.2  # mkz_example

    def __init__(self) -> None:
        self.violated_stop_sign_stopped_times = list()

        self.last_localization = None
        self.last_planning = None

        self.first_stop_timestamp = None

        self.violations = list()
        self.sorted_stop_sign_ids = sorted(MapParser.get_instance().get_stop_signs())

    def get_interested_topics(self):
        return [
            '/apollo/localization/pose',
            '/apollo/planning',
        ]

    def on_new_message(self, topic: str, message, t):
        if topic == '/apollo/localization/pose':
            self.last_localization = message
        else:
            self.last_planning = message
            return

        if self.last_localization is None or self.last_planning is None:
            return

        if not self.is_adc_completely_stopped():
            self.first_stop_timestamp = None
            return
        self.calculate_adc_stop_times_at_stop_signs()

    def is_adc_completely_stopped(self) -> bool:
        adc_pose = self.last_localization.pose
        adc_velocity = calculate_velocity(adc_pose.linear_velocity)

        # https://github.com/ApolloAuto/apollo/blob/0789b7ea1e1356dde444452ab21b51854781e304/modules/planning/scenarios/stop_sign/unprotected/stage_pre_stop.cc#L237
        # return adc_velocity <= self.MAX_ABS_SPEED_WHEN_STOPPED
        return adc_velocity == 0

    # the function below will handle the case that ADC stop too long at stop sign
    def calculate_adc_stop_times_at_stop_signs(self) -> None:
        if not self.is_planning_main_decision_to_stop_at_stop_sign(self.last_planning):
            self.first_stop_timestamp = None
            return

        last_stop_timestamp = self.last_localization.header.timestamp_sec
        if self.first_stop_timestamp is None:
            self.first_stop_timestamp = last_stop_timestamp

        adc_total_stop_time = last_stop_timestamp - self.first_stop_timestamp
        if adc_total_stop_time > self.ADC_MAX_STOP_TIME_ON_STOP_SIGN_IN_SECOND:
            last_stop_reason = self.last_planning.decision.main_decision.stop.reason
            # self.violated_stop_sign_stopped_times.append((adc_total_stop_time, str(last_stop_reason)))
            features = self.get_basic_info_from_localization(self.last_localization)
            features['reason_code'] = self.last_planning.decision.main_decision.stop.reason_code
            self.violations.append(Violation(
                'UUStopOracle',
                features,
                str(features['reason_code'])
            ))

    def is_planning_main_decision_to_stop_at_stop_sign(self, planning_message: ADCTrajectory) -> bool:
        try:
            stop_decision = planning_message.decision.main_decision.stop
        except AttributeError:
            return False

        stop_reason_code = stop_decision.reason_code
        if stop_reason_code == STOP_REASON_STOP_SIGN:
            return True

        return False

    def get_result(self):
        return self.violations
