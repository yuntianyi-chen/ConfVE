import json
from websocket import create_connection


class Dreamview:
    """
    Class to wrap Dreamview connection
    """

    def __init__(self, ip: str, port: int) -> None:
        """
        Constructs all the attributes for Dreamview object

        Parameters:
            ip: str
                ip address of Dreamview
            port: int
                port of Dreamview
        """
        self.url = f"ws://{ip}:{port}/websocket"
        # self.ws = create_connection(self.url)
        # self.start_sim_control()

    def send_data(self, data: dict):
        """
        Helper function to send data to Dreamview

        Parameters:
            data: dict
                data to be sent
        """
        self.ws.send(json.dumps(data))

    def start_sim_control(self):
        """
        Starts SimControl
        """
        data = {
            'type': 'ToggleSimControl',
            'enable': True
        }
        self.send_data(data)

    def stop_sim_control(self):
        """
        Stops SimControl
        """

        data = {
            'type': 'ToggleSimControl',
            'enable': False
        }
        self.send_data(data)

    def reset(self):
        """
        Resets Dreamview
        """
        self.ws = create_connection(self.url)
        self.start_sim_control()
