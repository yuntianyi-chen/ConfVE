from typing import Set
from objectives.violation_number.oracles.OracleInterface import OracleInterface
from objectives.violation_number.oracles.Violation import Violation


class EStopOracle(OracleInterface):
    """
    Emergency Stop Oracle is responsible for checking if the ADS made an emergency stop decision. This decision
    indicates a human driver should take over.
    Its features include:
        * x:            float
        * y:            float
        * heading:      float
        * speed:        float
        * reason_code:  int
    """
    estops: Set

    def __init__(self) -> None:
        self.estops = set()
        self.last_localization = None
        self.violations = list()

    def get_interested_topics(self):
        return [
            '/apollo/planning',
            '/apollo/localization/pose'
        ]

    def on_new_message(self, topic: str, message, t):
        if topic == '/apollo/planning':
            main_decision = message.decision.main_decision
            if main_decision.HasField('estop'):
                # self.estops.add(main_decision.estop.reason_code)
                features = self.get_basic_info_from_localization(self.last_localization)
                features['reason_code'] = main_decision.estop.reason_code
                self.violations.append(Violation(
                    'EStopOracle',
                    features,
                    str(features['reason_code'])
                ))
        else:
            self.last_localization = message

    def get_result(self):
        return self.violations
