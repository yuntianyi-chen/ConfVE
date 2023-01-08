import time
# from typing import List
from logging import Logger
from threading import Thread
from modules.common.proto.header_pb2 import Header
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles
# from apollo.utils import localization_to_obstacle, obstacle_to_polygon
# from apollo.CyberBridge import Channel, Topics
# from framework.scenario.PedestrianManager import PedestrianManager
from utils import get_logger
from config import PERCEPTION_FREQUENCY
from tools.bridge.CyberBridge import Channel, Topics
from tools.utils import localization_to_obstacle, obstacle_to_polygon


# from apollo.ApolloRunner import ApolloRunner


class MessageBroker:
    """
    Class to represent MessageBroker

    Attributes:
    runners: List[ApolloRunners]
        list of running Apollo instances
    spinning: bool
        whether the message broker should forward localization as obstacle
    logger: Logger
        logging the status of the message broker
    t: Thread
        background thread to forward data
    """
    # runners: List[ApolloRunner]
    # spinning: bool
    logger: Logger
    t: Thread

    def __init__(self, bridge, obs_perception_messages) -> None:
        """
        Constructs all the attributes for MessageBroker

        Parameters:
            runners: List[ApolloRunner]
                list of running Apollo instances
        """
        # self.runners = runners
        self.bridge = bridge
        # self.spinning = False
        # self.logger = get_logger('MessageBroker')

        self.obs_perception_messages = obs_perception_messages

    # def broadcast(self, channel: Channel, data: bytes):
    #     """
    #     Sends data to every instance
    #
    #     Parameters:
    #         channel: Channel
    #             channel to send data to
    #         data: bytes
    #             data to be sent
    #     """
    #     for runner in self.runners:
    #         runner.container.bridge.publish(channel, data)

    def register_perception(self):
        """
        Helper function to start forwarding localization
        """
        header_sequence_num = 0
        # curr_time = 0.0

        for obs_perception_message in self.obs_perception_messages:
        # while self.spinning:
            header = Header(
                timestamp_sec=time.time(),
                module_name='CONFIG_TESTING',
                sequence_num=header_sequence_num
            )
            bag = PerceptionObstacles(
                header=header,
                perception_obstacle=obs_perception_message,
            )

            self.bridge.publish(Topics.Obstacles, bag.SerializeToString())

            header_sequence_num += 1
            time.sleep(1 / PERCEPTION_FREQUENCY)
            # curr_time += 1 / PERCEPTION_FREQUENCY

    def start(self):
        """
        Starts to forward localization
        """
        # self.logger.debug('Starting to spin')
        # if self.spinning:
        #     return
        self.t = Thread(target=self.register_perception)
        # self.spinning = True
        self.t.start()

    def stop(self):
        """
        Stops forwarding localization
        """
        # self.logger.debug('Stopping')
        # if not self.spinning:
        #     return
        # self.spinning = False
        self.t.join()
