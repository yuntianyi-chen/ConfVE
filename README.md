ADS Configuration Testing Framework

0. Prerequisite: Install the required Python libraries: numpy, Shapely, pandas, networkx, docker, and cyber_record
1. Replace `dev_start.sh` file with the script under `/data/scripts/apollo_multi_container/`
2. Start your container with `dev_start.sh`, build your apollo system using instructions in the official website
3. Change the IMPORTANT CONFIGURATION and DIR values in `config.py` according to your environment. Place the project under `DIR_ROOT`
4. Place initial records under `/data/records`, run `prepare.py`
4. Run `python3 main.py`