import os
import time
import docker
import signal
import subprocess
from environment.Dreamview import Dreamview
from tools.bridge.CyberBridge import CyberBridge, Topics
from scenario_handling.MessageHandler import MessageHandler


class Container:
    """
    Class to represent Apollo container

    Attributes:
    apollo_root: str
        Root directory of Baidu Apollo
    username: str
        Unique id used to identify container
    bridge: CyberBridge
        Used to connect to cyber bridge
    dreamview: Dreamview
        Websocket connection to control Dreamview
    port: int
        Network port for Dreamview
    bridge_port: int
        Network port for cyber bridge
    """
    apollo_root: str
    username: str
    bridge: CyberBridge
    dreamview: Dreamview
    port = 8888
    bridge_port = 9090

    def __init__(self, apollo_root: str, username: str) -> None:
        """
        Constructs all the attributes for ApolloContainer object

        Parameters:
            apollo_root: str
                Root directory of Baidu Apollo
            username: str
                Unique id used to identify container
        """
        self.apollo_root = apollo_root
        self.username = username

    @property
    def container_name(self) -> str:
        """
        Gets the name of the container

        Returns:
            name: str
                name of the container
        """
        return f"apollo_dev_{self.username}"

    def is_running(self) -> bool:
        """
        Checks if the container is running

        Returns:
            status: bool
                True if running, False otherwise
        """
        try:
            return docker.from_env().containers.get(self.container_name).status == 'running'
        except:
            return False

    @property
    def ip(self) -> str:
        """
        Gets the ip address of the container

        Returns:
            ip: str
                ip address of the container
        """
        assert self.is_running(
        ), f'Instance {self.container_name} is not running.'
        ctn = docker.from_env().containers.get(self.container_name)
        return ctn.attrs['NetworkSettings']['IPAddress']

    def start_instance(self, restart=False):
        """
        Starts an Apollo instance

        Parameters:
            restart : bool
                forcing container to restart
        """
        if not restart and self.is_running():
            return
        cmd = f'bash {self.apollo_root}/docker/scripts/dev_start.sh -l -y'
        subprocess.run(
            cmd.split(),
            env={
                'USER': self.username
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def __dreamview_operation(self, op: str):
        """
        Helper function to start/stop/restart Dreamview

        Parameters:
            op: str
                Operation can be one of [start, stop, restart]
        """
        ops = {
            'start': ('Starting', 'start', f'Running Dreamview at http://{self.ip}:{self.port}'),
            'stop': ('Stopping', 'stop', f'Stopped Dreamview'),
            'restart': ('Restarting', 'restart', f'Restarted Dreamview at http://{self.ip}:{self.port}')
        }
        s0, s1, s2 = ops[op]
        cmd = f"docker exec {self.container_name} ./scripts/bootstrap.sh {s1}"
        subprocess.run(cmd.split(), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

        time.sleep(1)

        if op == 'stop':
            self.dreamview = None
        else:
            self.dreamview = Dreamview(self.ip, self.port)

    def start_dreamview(self):
        """
        Start Dreamview
        """
        self.__dreamview_operation('start')

    def stop_dreamview(self):
        """
        Stop Dreamview
        """
        self.__dreamview_operation('stop')

    def start_sim_control_standalone(self):
        """
        Starts SimControlStandalone module
        """
        cmd = f"docker exec -d {self.container_name} /apollo/bazel-bin/modules/sim_control/sim_control_main"
        subprocess.run(
            cmd.split(),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    def stop_sim_control_standalone(self):
        """
        Stops SimControlStandalone module
        """
        cmd = f"docker exec {self.container_name} /apollo/modules/sim_control/script.sh stop"
        subprocess.run(
            cmd.split(),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    def create_message_handler(self, map_instance):
        self.message_handler = MessageHandler(self.bridge, map_instance)

    def connect_bridge(self):
        self.bridge = self.start_bridge_simply()
        self.register_bridge_publishers()

    def start_bridge_simply(self):
        cmd = f"docker exec -d {self.container_name} /apollo/scripts/bridge.sh"
        subprocess.run(cmd.split())

        while True:
            try:
                docker_container_ip = self.get_docker_container_ip()
                bridge = CyberBridge(docker_container_ip, 9090)
                return bridge
            except ConnectionRefusedError:
                time.sleep(1)

    def register_bridge_publishers(self):
        for c in [Topics.Localization, Topics.Obstacles, Topics.TrafficLight, Topics.RoutingRequest]:
            self.bridge.add_publisher(c)

    def get_docker_container_ip(self):
        docker_container_info = docker.from_env().containers.get(self.container_name)
        return docker_container_info.attrs['NetworkSettings']['IPAddress']

    def cyber_env_init(self):
        # print("Killing modules...")
        self.kill_modules()

        # print("Killing Dreamview...")
        self.close_subprocess()

        # print("Starting Dreamview...")
        self.start_dreamview()

        # print("Starting modules...")
        self.modules_operation(operation="start")

    def restart_dreamview(self):
        self.close_subprocess()
        self.start_dreamview()

    def restart_modules(self):
        self.modules_operation(operation="stop")
        self.kill_modules()
        self.modules_operation(operation="start")

    def close_subprocess(self):
        cmd = f"docker exec -d {self.container_name} /apollo/scripts/my_scripts/close_subprocess.sh"
        subprocess.run(cmd.split())

    def kill_modules(self):
        cmd = f"docker exec -d {self.container_name} bash /apollo/scripts/my_scripts/kill_modules.sh"
        subprocess.run(cmd.split())

    def dreamview_operation(self, operation):
        cmd = f"docker exec -d {self.container_name} bash /apollo/scripts/bootstrap.sh {operation}"
        subprocess.run(cmd.split())
        if operation == "start" or "restart":
            time.sleep(5)
        else:
            time.sleep(1)

    def modules_operation(self, operation):
        cmd = f"docker exec -d {self.container_name} bash /apollo/scripts/routing.sh {operation}"
        subprocess.run(cmd.split())
        cmd = f"docker exec -d {self.container_name} bash /apollo/scripts/planning.sh {operation}"
        subprocess.run(cmd.split())
        cmd = f"docker exec -d {self.container_name} bash /apollo/scripts/prediction.sh {operation}"
        subprocess.run(cmd.split())

    def start_recorder(self, record_name):
        cmd = f"docker exec -d {self.container_name} /apollo/bazel-bin/cyber/tools/cyber_recorder/cyber_recorder record -o /apollo/records/{record_name} -a &"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop_recorder(self):
        cmd = f"docker exec -d {self.container_name} /apollo/scripts/my_scripts/stop_recorder.sh"
        subprocess.run(cmd.split())

    def stop_subprocess(self, p):
        try:
            os.kill(p.pid, signal.SIGINT)
            p.kill()
        except OSError:
            print("stopped")
