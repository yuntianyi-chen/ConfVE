ADS Configuration Testing Framework

1. Replace `dev_start.sh` file with the script under `/data/scripts/apollo_multi_container/`
2. Start your container with `dev_start.sh`, build your apollo system using instructions in the official website
3. Change the IMPORTANT CONFIGURATION and DIR values in `config.py` according to your environment. Place some records under `INITIAL_SCENARIO_RECORD_DIR`
4. Run `main.py`