import time
from logging import Logger
from threading import Thread
from modules.common.proto.header_pb2 import Header
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles
from config import PERCEPTION_FREQUENCY, TRAFFIC_LIGHT_FREQUENCY, TRAFFIC_LIGHT_MODE
from modules.perception.proto.traffic_light_detection_pb2 import TrafficLightDetection
from scenario_handling.traffic_light_control.TrafficControlManager import TrafficControlManager
from tools.bridge.CyberBridge import Topics



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
    t_obs: Thread
    t_traffi : Thread

    def __init__(self, bridge) -> None:
        """
        Constructs all the attributes for MessageBroker

        Parameters:
            runners: List[ApolloRunner]
                list of running Apollo instances
        """
        # self.runners = runners
        self.bridge = bridge
        self.obs_is_running = False
        self.traffic_is_running = False
        # self.logger = get_logger('MessageBroker')

        # self.obs_perception_messages = obs_perception_messages

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

    def register_obs_perception(self):
        """
        Helper function to start forwarding localization
        """
        header_sequence_num = 0
        # curr_time = 0.0

        index =0
        while self.obs_is_running and index < len(self.obs_perception_messages):
            # while self.spinning:
            header = Header(
                timestamp_sec=time.time(),
                module_name='CONFIG_TESTING_OBS',
                sequence_num=header_sequence_num
            )

            bag = PerceptionObstacles(
                header=header,
                perception_obstacle=self.obs_perception_messages[index],
            )

            self.bridge.publish(Topics.Obstacles, bag.SerializeToString())

            header_sequence_num += 1
            index+=1
            time.sleep(1 / PERCEPTION_FREQUENCY)
            # curr_time += 1 / PERCEPTION_FREQUENCY


    def update_obs_msg(self, obs_perception_messages):
        self.obs_perception_messages = obs_perception_messages




    def obs_start(self):
        # self.logger.debug('Starting to spin')
        # if self.spinning:
        #     return
        self.t_obs = Thread(target=self.register_obs_perception)
        self.obs_is_running = True
        self.t_obs.start()

    def obs_stop(self):
        # self.logger.debug('Stopping')
        # if not self.spinning:
        #     return
        self.obs_is_running = False

        # wait for the new thread to stop
        self.t_obs.join()

    def update_traffic_msg(self, traffic_control):
        if TRAFFIC_LIGHT_MODE == "read":
            self.traffic_control_msg = traffic_control
        elif TRAFFIC_LIGHT_MODE == "random":
            self.traffic_control_manager = traffic_control

    def register_traffic_lights(self):
        # tm = TrafficControlManager(traffic_light_control)
        runner_time = 0
        index = 0
        header_sequence_num = 0

        while self.traffic_is_running and index < len(self.traffic_control_msg):
            # Publish TrafficLight
            if TRAFFIC_LIGHT_MODE == "read":
                header = Header(
                    timestamp_sec=time.time(),
                    module_name='CONFIG_TESTING_TRAFFIC',
                    sequence_num=header_sequence_num
                )
                tld = TrafficLightDetection(
                    header=header,
                    traffic_light=self.traffic_control_msg[index],
                )
                # tld = self.traffic_control_msg[index]
            elif TRAFFIC_LIGHT_MODE == "random":
                tld = self.traffic_control_manager.get_traffic_configuration(runner_time / 1000)
            else:
                tld = None



            self.bridge.publish(Topics.TrafficLight, tld.SerializeToString())

            # Check if scenario exceeded upper limit
            # if runner_time / 1000 >= MAX_RECORD_TIME:
            #     break
            header_sequence_num += 1
            index +=1
            time.sleep(1 / TRAFFIC_LIGHT_FREQUENCY)
            runner_time += 100

    def traffic_lights_start(self):
        # self.logger.debug('Starting to spin')
        # if self.spinning:
        #     return
        self.t_traffic = Thread(target=self.register_traffic_lights)
        self.traffic_is_running = True
        self.t_traffic.start()

    def traffic_lights_stop(self):
        # self.logger.debug('Stopping')
        # if not self.spinning:
        #     return
        self.traffic_is_running = False

        # wait for the new thread to stop
        self.t_traffic.join()


