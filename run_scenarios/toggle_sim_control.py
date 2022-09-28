#!/usr/bin/python3

import json
import asyncio
import websockets

async def handle_commandline(websocket):
#     while True:
     #    cmd = input("Please enter your command(help):")
     cmd = "start simcontrol"
     if cmd == "exit":
          print('Bye')
          await websocket.close(reason="exit")
          return False
     elif cmd == "help":
          print('Supported commands:')
          print('\tstart simcontrol')
          print('\tstop simcontrol')
          print('\texit')
     elif cmd == "start simcontrol":
          data = {
               'type': 'ToggleSimControl',
               'enable': True
          }
          jsonstr = json.dumps(data)
          print('Output json: ', jsonstr)
          await websocket.send(jsonstr)
     elif cmd == "stop simcontrol":
          data = {
               'type': 'ToggleSimControl',
               'enable': False
          }
          jsonstr = json.dumps(data)
          print('Output json: ', jsonstr)
          await websocket.send(jsonstr)
     else:
          print('Invalid command')

async def event_handler():
    async with websockets.connect('ws://127.0.0.1:8888/websocket') as websocket:
        await handle_commandline(websocket)

asyncio.get_event_loop().run_until_complete(event_handler())
# event_handler()
