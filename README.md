ADS Configuration Testing Framework

0. Prerequisite: Install the required Python libraries: numpy, Shapely, pandas, networkx, docker, and cyber_record using `pip install -r requirements.txt`. 
    Using Apollo 7.0 from our project (https://github.com/yuntianyi-chen/apollo-baidu/tree/deploy) is recommended. Remember to use `git checkout deploy` to switch to the deploy branch
1. Replace the file `apollo_baidu/docker/scripts/dev_start.sh` with the file under `ConfVE/data/scripts/apollo_multi_container/dev_start.sh`, Place the `ConfVE` under the same directory with `apollo_baidu`
2. Start your container with `bash docker/scripts/dev_start.sh` or `./apollo.sh dev_start.sh`, build your apollo system using instructions in the official website
3. Change the parameters in `config.py` according to your requirements
4. Place directories of initial record files under `ConfVE/data/records`, run `tools/script/prepare.py`
5. Execute `sudo chmod -R 777 apollo_baidu/data`
6. Run `python3 main.py`
