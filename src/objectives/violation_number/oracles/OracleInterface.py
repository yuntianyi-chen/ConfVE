from abc import ABC, abstractmethod
from typing import List
from modules.localization.proto.localization_pb2 import LocalizationEstimate
from tools.utils import calculate_velocity


class OracleInterface(ABC):

    @abstractmethod
    def get_interested_topics(self) -> List[str]:
        return list()

    @abstractmethod
    def on_new_message(self, topic: str, message, t):
        pass

    @abstractmethod
    def get_result(self):
        return list()

    @staticmethod
    def get_dummy_basic_info():
        return {
            'x': 0,
            'y': 0,
            'heading': 0,
            'speed': 0
        }

    @staticmethod
    def get_basic_info_from_localization(message: LocalizationEstimate):
        speed = calculate_velocity(message.pose.linear_velocity)
        features = {
            'x': message.pose.position.x,
            'y': message.pose.position.y,
            'heading': message.pose.heading,
            'speed': speed,
        }
        return features
