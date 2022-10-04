import subprocess
import time

import docker

from apollo.CyberBridge import CyberBridge, Topics
from environment.container_settings import get_container_name
from scenario_handling.toggle_sim_control import run_sim_control


def cyber_env_init():
    print("Init cyber environment...")
    dreamview_operation(operation="restart")
    # modules_operation(operation="start")
    print("Start sim control...")
    run_sim_control()
    print("Start bridge...")
    bridge = start_bridge()
    # cyber_setup()

    register_bridge_publishers(bridge)
    return bridge


def register_bridge_publishers(bridge):
    for c in [Topics.Localization, Topics.Obstacles, Topics.TrafficLight, Topics.RoutingRequest]:
        bridge.add_publisher(c)


def dreamview_operation(operation):
    cmd = f"docker exec -d {get_container_name()} bash /apollo/scripts/bootstrap.sh {operation}"
    subprocess.run(cmd.split())
    if operation == "start" or "restart":
        time.sleep(10)
    else:
        time.sleep(1)


def modules_operation(operation):
    cmd = f"docker exec -d {get_container_name()} bash /apollo/scripts/prediction.sh {operation}"
    subprocess.run(cmd.split())
    cmd = f"docker exec -d {get_container_name()} bash /apollo/scripts/planning.sh {operation}"
    subprocess.run(cmd.split())
    cmd = f"docker exec -d {get_container_name()} bash /apollo/scripts/routing.sh {operation}"
    subprocess.run(cmd.split())
    time.sleep(1)


def cyber_setup():
    time.sleep(1)
    cmd = f"docker exec -d {get_container_name()} source /apollo/cyber/setup.bash"
    subprocess.run(cmd.split())
    time.sleep(1)


def get_docker_container_ip():
    """
    Gets the ip address of the container

    Returns:
        ip: str
            ip address of the container
    """
    ctn = docker.from_env().containers.get(get_container_name())
    return ctn.attrs['NetworkSettings']['IPAddress']


def start_bridge():
    cmd = f"docker exec -d {get_container_name()} /apollo/scripts/bridge.sh"
    subprocess.run(cmd.split())

    while True:
        try:
            docker_container_ip = get_docker_container_ip()

            bridge = CyberBridge(docker_container_ip, 9090)
            return bridge
        except ConnectionRefusedError:
            time.sleep(1)
