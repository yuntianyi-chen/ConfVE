import time
from threading import Thread
from modules.common.proto.header_pb2 import Header
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles
from config import PERCEPTION_FREQUENCY, TRAFFIC_LIGHT_FREQUENCY, TRAFFIC_LIGHT_MODE
from modules.perception.proto.traffic_light_detection_pb2 import TrafficLightDetection
from environment.cyber_env_operation import connect_bridge
from tools.bridge.CyberBridge import Topics


class MessageHandler:

    def __init__(self) -> None:
        bridge = connect_bridge()
        self.bridge = bridge
        self.obs_is_running = False
        self.traffic_is_running = False

    def register_obs_perception(self):
        header_sequence_num = 0
        index = 0
        while self.obs_is_running and index < len(self.obs_perception_messages):
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
            index += 1
            time.sleep(1 / PERCEPTION_FREQUENCY)

    def update_obs_msg(self, obs_perception_messages):
        self.obs_perception_messages = obs_perception_messages

    def obs_start(self):
        self.t_obs = Thread(target=self.register_obs_perception)
        self.obs_is_running = True
        self.t_obs.start()

    def obs_stop(self):
        self.obs_is_running = False
        self.t_obs.join()

    def update_traffic_msg(self, traffic_control):
        if TRAFFIC_LIGHT_MODE == "read":
            self.traffic_control_msg = traffic_control
        elif TRAFFIC_LIGHT_MODE == "random":
            self.traffic_control_manager = traffic_control

    def register_traffic_lights(self):
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
            elif TRAFFIC_LIGHT_MODE == "random":
                tld = self.traffic_control_manager.get_traffic_configuration(runner_time / 1000)
            else:
                tld = None

            self.bridge.publish(Topics.TrafficLight, tld.SerializeToString())
            header_sequence_num += 1
            index += 1
            time.sleep(1 / TRAFFIC_LIGHT_FREQUENCY)
            runner_time += 100

    def traffic_lights_start(self):
        self.t_traffic = Thread(target=self.register_traffic_lights)
        self.traffic_is_running = True
        self.t_traffic.start()

    def traffic_lights_stop(self):
        self.traffic_is_running = False
        self.t_traffic.join()
