import subprocess

from environment.container_settings import get_container_name

cmd = f"docker exec -d {get_container_name()} /apollo/bazel-bin/cyber/tools/cyber_recorder/cyber_recorder play -f /apollo/records/Generation36_Scenario33.00000 -c /apollo/perception/obstacles -l"
subprocess.run(cmd.split())