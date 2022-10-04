import subprocess

from environment.container_settings import get_container_name

cmd = f"docker exec -d {get_container_name()} cyber_recorder record -o /apollo/records/asdsad -a &"
subprocess.Popen(cmd.split(), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


cmd = f"docker exec -d {get_container_name()} python3 /apollo/scripts/record_bag.py --stop --stop_signal SIGINT > /dev/null 2>&1"
subprocess.run(cmd.split())

# docker exec -d apollo_dev_cloudsky /apollo/modules/tools/perception/obstacles_perception.bash /apollo/modules/tools/perception/obstacles/sunnyvale_loop/obs_group_0