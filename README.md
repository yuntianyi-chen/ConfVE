ADS Configuration Testing Framework

## Prerequisite
- Install the required Python libraries: numpy, Shapely, pandas, networkx, docker, and cyber_record using `pip install -r requirements.txt`. 
- Using Apollo 7.0 is recommended. 

## Environment Setup
1. Install Apollo 7.0 from official website and name the root directory `/apollo`
1. Place the `/ConfVE` under the same directory with `/apollo`
1. Copy the directory `module/sim_control` to `apollo/modules/`
2. Replace the file `apollo/docker/scripts/dev_start.sh` with the file under `ConfVE/data/scripts/apollo_multi_container/dev_start.sh`, 
3. Start the docker container using `bash docker/scripts/dev_start.sh`
3. Enter the docker container using `bash docker/scripts/dev_into.sh`
4. Build the apollo system using `./apollo.sh build` or `./apollo.sh build_opt_gpu`

## Usage
1. Change the parameters in `config.py` according to your requirements
2. Place directories of initial record files under `ConfVE/data/records`, run `tools/script/prepare.py`
3. Execute `sudo chmod -R 777 apollo/data` to change the permission of the directory `apollo/data`
4. Run `python3 main.py` to start the testing

## Notice
- For the first run, the map parser would be automated executed to generate and save the map info file. If you test on a large map, it may take a long time.