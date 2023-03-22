import subprocess
from config import APOLLO_ROOT
from environment.Container import Container
from environment.MapLoader import MapLoader
from objectives.violation_number.oracles import RecordAnalyzer

if __name__ == '__main__':
    replay_record_name = "Generation_4_Config_16_Scenario_46"

    replay_record_path = f"/apollo/initial/test/{replay_record_name}.00000"
    replay_record_path_abs = f"{APOLLO_ROOT}/initial/test/{replay_record_name}.00000"

    ctn = Container(APOLLO_ROOT, f'cloudsky')
    map_instance = MapLoader().map_instance

    # ctn.start_instance()
    # ctn.cyber_env_init()
    # ctn.connect_bridge()

    print(f'Dreamview at http://{ctn.ip}:{ctn.port}')

    ra = RecordAnalyzer(replay_record_path_abs)
    violation_results = ra.analyze()

    print(violation_results)
    cmd = f"docker exec -d {ctn.container_name} /apollo/bazel-bin/cyber/tools/cyber_recorder/cyber_recorder play -f {replay_record_path}"
    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
