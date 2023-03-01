ADS Configuration Testing Framework

0. Prerequisite: Install the required Python libraries: numpy, Shapely, pandas, networkx, docker, and cyber_record. 
    Using Apollo 7.0 from our project (https://github.com/yuntianyi-chen/apollo-baidu/tree/deploy) is recommended.
1. Replace the file `apollo/docker/scripts/dev_start.sh` with the file under `{project}/data/scripts/apollo_multi_container/dev_start.sh`
2. Start your container with `./apollo.sh dev_start.sh`, build your apollo system using instructions in the official website
3. Change the IMPORTANT CONFIGURATION and DIR values in `config.py` according to your environment. Place the project under `DIR_ROOT`
4. Place initial record files under `{project}/data/records`, run `tools/script/prepare.py`
5. Execute `sudo chmod -R 777 apollo/data`
6. Run `python3 main.py`
