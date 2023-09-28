import subprocess

from environment.Container import Container
from environment.MapLoader import MapLoader

apollo_root = "/home/cloudsky/Research/Apollo/Benchmark/apollo"
ctn = Container(apollo_root, f'')

map_instance = None
# ctn.start_instance()
# ctn.cyber_env_init()
ctn.connect_bridge()
ctn.create_message_handler(map_instance)

print(f'Dreamview at http://{ctn.ip}:{ctn.port}')


def publish_routing():
    cmd = f"docker exec -d apollo_dev bash /apollo/scripts/prediction.sh {operation}"
    subprocess.run(cmd.split())


def publish_traffic_lights():
    cmd = f"docker exec -d apollo_dev bash /apollo/scripts/prediction.sh {operation}"
    subprocess.run(cmd.split())


def publish_obstacles():
    cmd = f"docker exec -d apollo_dev bash /apollo/scripts/prediction.sh {operation}"
    subprocess.run(cmd.split())


"/apollo/modules/tools/perception/garage_perception.bash"