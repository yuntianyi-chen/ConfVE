from cyber_record.record import Record
from objectives.violation_number.oracles.OracleManager import OracleManager
from objectives.violation_number.oracles.impl.CollisionOracle import CollisionOracle
from objectives.violation_number.oracles.impl.ComfortOracle import ComfortOracle
from objectives.violation_number.oracles.impl.ModuleDelayOracle import ModuleDelayOracle
from objectives.violation_number.oracles.impl.ModuleOracle import ModuleOracle
from objectives.violation_number.oracles.impl.SpeedingOracle import SpeedingOracle
from objectives.violation_number.oracles.impl.UnsafeLaneChangeOracle import UnsafeLaneChangeOracle
from objectives.violation_number.oracles.impl.JunctionLaneChangeOracle import JunctionLaneChangeOracle


class RecordAnalyzer:
    record_path: str

    def __init__(self, record_path: str) -> None:
        self.oracle_manager = OracleManager()
        self.record_path = record_path
        self.register_oracles()

    def register_oracles(self):
        oracles = [
            CollisionOracle(),
            UnsafeLaneChangeOracle(),
            SpeedingOracle(),
            ComfortOracle(),
            ModuleOracle(),
            ModuleDelayOracle(),
            JunctionLaneChangeOracle()
        ]
        for o in oracles:
            self.oracle_manager.register_oracle(o)

    def analyze(self):
        record = Record(self.record_path)
        for topic, message, t in record.read_messages():
            self.oracle_manager.on_new_message(topic, message, t)
        return self.get_results()

    def get_results(self):
        return self.oracle_manager.get_results()
