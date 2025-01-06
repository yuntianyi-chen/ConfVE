# ConfVE

## Introduction

ConfVE (Configuration Violation Emerger) is the first configuration testing approach in the ADS domain, which serves as a testing framework that utilizes scenarios from pre-existing ADS scenario-generation techniques and a genetic algorithm to produce alternative configurations to identify emerged failures in an ADS by preventing the masking of failures and maximizing the possibility of producing bug-revealing violations.

The **published paper** of ConfVE is available at [ACM FSE 2024](https://doi.org/10.1145/3660792)

The **video recordings** of ConfVE when different types of violations happen are available at [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.11051748.svg)](https://doi.org/10.5281/zenodo.11051748)

## Hardware and Software Requirements

- Intel Core i9 12900K (16-core)

- 96 GB memory and above

- Ubuntu 22.04 and above

- Docker-CE version 19.03 and above

- Python 3.11 and above

- NVIDIA RTX 3090 and above **(Optional)**

- NVIDIA driver version 455.32.00 and above **(Optional)**

- NVIDIA Container Toolkit **(Optional)**

### Additional Information

ConfVE runs multiple Docker container simultaneously, therefore the requirement for running ConfVE varies based on the number of containers (default=5) you wish to run.

## Installing

In this section we will be discussing steps to replicate the results discussed in the paper

```
|--DIR_ROOT
    |--apollo
        |--modules
        |...
    |--ConfVE
        |--data
        |--src
            |--config.py
            |--main.py
```

1. Git clone this repository or download the zip file of this project. Unzip the `ConfVE.zip` file to get the `data` and `src` directories.

2. Place the `/ConfVE` under the same directory with `/apollo`

### INSTALLING Apollo ADS

1. Git clone or Download the Apollo 7.0 from https://github.com/yuntianyi-chen/apollo-baidu/tree/master, and name the apollo root directory `/apollo`

2. Copy the directory `ConfVE/data/module/sim_control` to `apollo/modules/`

3. Replace the file `apollo/docker/scripts/dev_start.sh` with the file of `ConfVE/data/scripts/apollo_multi_container/dev_start.sh`, 

4. At the root directory of Apollo, start up Apollo container via `bash docker/scripts/dev_start.sh`

5. Enter the docker container using `bash docker/scripts/dev_into.sh`

6. In the container, build Apollo via `./apollo.sh build` or `./apollo.sh build_opt_gpu`

### INSTALLING ConfVE

1. Enter the `ConfVE` folder, install the required Python libraries via `pip install -r requirements.txt`. This includes installing the required Python libraries: numpy, Shapely, pandas, networkx, docker, and cyber_record.

2. Customize the parameters in `ConfVE/src/config.py` according to your requirements, or just remain default.

3. Place your directories of initial record files under `ConfVE/data/records`, run `python3 prepare.py`

> The folder name should follow the rule of `ApproachName_MapName`(e.g., `DoppelTest_borregas_ave`). We've provided a group of sample records file under `ConfVE/data/records` for your reference.

4. Execute `sudo chmod -R 777 apollo/data` to change the permission of the directory `apollo/data`

5. Run `python3 main.py` to start the testing

> After running ConfVE for extended period of time, you should see temporary record files of scenarios generated under `apollo/data/records`. This is also the step to replicate the results presented in the paper.

### Notice
- For the first run, the map parser would be automated executed to generate and save the map info file. If you test on a large map, it may take a long time.


### Paper Citation
```aiignore
@article{ChenHLHG24,
  author       = {Yuntianyi Chen and
                  Yuqi Huai and
                  Shilong Li and
                  Changnam Hong and
                  Joshua Garcia},
  title        = {Misconfiguration Software Testing for Failure Emergence in Autonomous
                  Driving Systems},
  journal      = {Proc. {ACM} Softw. Eng.},
  volume       = {1},
  number       = {{FSE}},
  pages        = {1913--1936},
  year         = {2024},
  url          = {https://doi.org/10.1145/3660792},
  doi          = {10.1145/3660792},
  timestamp    = {Fri, 02 Aug 2024 21:41:21 +0200},
  biburl       = {https://dblp.org/rec/journals/pacmse/ChenHLHG24.bib},
  bibsource    = {dblp computer science bibliography, https://dblp.org}
}
```

