# import subprocess
# import time
# import docker
# from environment.container_settings import get_container_name
# from environment.toggle_sim_control import run_sim_control
# from tools.bridge.CyberBridge import Topics, CyberBridge

#
# def cyber_env_init():
#     print("Closing modules & Dreamview...")
#     modules_operation(operation="stop")
#     close_subprocess()
#     print("Restart Dreamview...")
#     dreamview_operation(operation="start")
#     print("Start sim control...")
#     run_sim_control()
#     print("Restarting modules...")
#     # kill_modules()
#     modules_operation(operation="start")
#
#
#
#
#
# def close_subprocess():
#     cmd = f"docker exec -d {get_container_name()} /apollo/scripts/my_scripts/close_subprocess.sh"
#     subprocess.run(cmd.split())
#
#
# def dreamview_operation(operation):
#     cmd = f"docker exec -d {get_container_name()} bash /apollo/scripts/bootstrap.sh {operation}"
#     subprocess.run(cmd.split())
#     if operation == "start" or "restart":
#         time.sleep(5)
#     else:
#         time.sleep(1)
#
#
# def modules_operation(operation):
#     cmd = f"docker exec -d {get_container_name()} bash /apollo/scripts/routing.sh {operation}"
#     subprocess.run(cmd.split())
#     time.sleep(0.5)
#     cmd = f"docker exec -d {get_container_name()} bash /apollo/scripts/planning.sh {operation}"
#     subprocess.run(cmd.split())
#     time.sleep(0.5)
#     cmd = f"docker exec -d {get_container_name()} bash /apollo/scripts/prediction.sh {operation}"
#     subprocess.run(cmd.split())
#     time.sleep(3)
#




# def kill_modules():
#     cmd = f"docker exec -d {get_container_name()} bash /apollo/scripts/my_scripts/kill_modules.sh"
#     subprocess.run(cmd.split())
#     time.sleep(1)

# def start_bridge():
#     cmd = f"docker exec -d {get_container_name()} /apollo/scripts/bridge.sh"
#     subprocess.run(cmd.split())
#
#     while True:
#         try:
#             docker_container_ip = get_docker_container_ip()
#             bridge = CyberBridge(docker_container_ip, 9090)
#             return bridge
#         except ConnectionRefusedError:
#             time.sleep(1)


# def cyber_setup():
#     cmd = f"docker exec -d {get_container_name()} source /apollo/cyber/setup.bash"
#     subprocess.run(cmd.split())
#     time.sleep(1)


# def get_docker_container_ip():
#     docker_container_info = docker.from_env().containers.get(get_container_name())
#     return docker_container_info.attrs['NetworkSettings']['IPAddress']


# def register_bridge_publishers(bridge):
#     for c in [Topics.Localization, Topics.Obstacles, Topics.TrafficLight, Topics.RoutingRequest]:
#         bridge.add_publisher(c)


# def connect_bridge():
#     print("Start bridge...")
#     bridge = start_bridge()
#     register_bridge_publishers(bridge)
#     return bridge