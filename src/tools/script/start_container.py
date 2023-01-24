from config import OPT_MODE, APOLLO_ROOT, CONTAINER_NUM
from environment.Container import Container
from environment.MapLoader import MapLoader
from time import sleep, time
from modules.common.proto.header_pb2 import Header
from modules.common.proto.geometry_pb2 import PointENU
from modules.localization.proto.localization_pb2 import LocalizationEstimate
from modules.routing.proto.routing_pb2 import RoutingRequest, LaneWaypoint

from modules.routing.proto.routing_pb2 import RoutingRequest
from tools.bridge.CyberBridge import Topics

if __name__ == '__main__':
    containers = [Container(APOLLO_ROOT, f'ROUTE_{x}') for x in range(1)]
    map_instance = MapLoader().map_instance

    for ctn in containers:
        ctn.start_instance()
        ctn.cyber_env_init()
        ctn.connect_bridge()
        ctn.create_message_handler(map_instance)

        # ctn.message_handler.send_initial_localization()
        print(f'Dreamview at http://{ctn.ip}:{ctn.port}')

        ctn.stop_sim_control_standalone()
        ctn.start_sim_control_standalone()

        for i in range(5):
            localization_message = LocalizationEstimate()
            localization_message.header.sequence_num = i
            localization_message.header.module_name = 'Reproduction'
            localization_message.header.timestamp_sec = time()
            localization_message.pose.position.x = 586952.4339599609
            localization_message.pose.position.y = 4141242.6538391113
            localization_message.pose.heading = -0.3024105043029949

            ctn.bridge.publish(Topics.Localization, localization_message.SerializeToString())
            sleep(0.5)


        routing_request = RoutingRequest()
        routing_request.header.sequence_num = 0
        routing_request.header.module_name = 'Reproduction'
        routing_request.header.timestamp_sec = time()

        routing_request = RoutingRequest(
            header=Header(
                timestamp_sec=time(),
                module_name="Reproduction",
                sequence_num=0
            ),
            waypoint=[
                LaneWaypoint(
                    pose=PointENU(
                        x=586952.4339599609,
                        y=4141242.6538391113,
                    ),
                ),
                LaneWaypoint(
                    pose=PointENU(
                        x=586993.905385346,
                        y=4141232.039176395
                    )
                )
            ]
        )
        sleep(2)
        ctn.bridge.publish(Topics.RoutingRequest, routing_request.SerializeToString())




