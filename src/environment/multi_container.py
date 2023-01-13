from apollo.ApolloContainer import ApolloContainer
from utils import get_logger
from hdmap.MapParser import MapParser
from config import HD_MAP_PATH, APOLLO_ROOT
import shutil

logger = get_logger('MAIN')
mp = MapParser(HD_MAP_PATH)

containers = [ApolloContainer(APOLLO_ROOT, f'ROUTE_{x}') for x in range(3)]
for ctn in containers:
    ctn.start_instance()
    ctn.stop_modules()
    ctn.start_dreamview()
    ctn.dreamview.start_sim_control()
    print(f'Dreamview at http://{ctn.ip}:{ctn.port}')

ctn0, ctn1, ctn2 = containers
routing_request = {
    "type":"SendRoutingRequest",
    "start":{
        "x":586953.5852661133,
        "y":4141198.2265625,
        "z":0,
        "heading":1.2937648030714186
    },
    "end":{
        "x":587038.2448794986,
        "y":4141515.538505184,
        "z":0
    },
    "waypoint":[]
    }

a = '/home/yuqi/ResearchWorkspace/BaiduApollo/DoppelTest_Apollo/modules/planning/conf/planning_config.pb.txt'
b = '/home/yuqi/ResearchWorkspace/BaiduApollo/DoppelTest_Apollo/modules/planning/conf/_planning_config.pb.txt'

testing = True

ctn0.start_modules()
ctn0.dreamview.send_data(routing_request)
print('ctn0 started')

if testing:
    shutil.move(a, b)

ctn1.start_modules()
ctn1.dreamview.send_data(routing_request)
print('ctn1 started')

if testing:
    shutil.move(b,a)

ctn2.start_modules()
ctn2.dreamview.send_data(routing_request)
print('ctn2 started')

# ctn0.start_recorder('ctn0')
# ctn1.start_recorder('ctn1')
# ctn2.start_recorder('ctn2')