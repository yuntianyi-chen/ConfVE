import glob
import os
import shutil
import subprocess
import time
from datetime import date
from pathlib import Path

from config import MAGGIE_ROOT, OBS_DIR, APOLLO_RECORDS_DIR

obs_folder = OBS_DIR + "scenorita"
temp_obs_dir = f"/home/cloudsky/Research/Apollo/Backup/scenoRITA/temp_obstacles"
backup_obs_dir = f"/home/cloudsky/Research/Apollo/Backup/scenoRITA/obstacles/{date.today()}"
shutil.copytree(temp_obs_dir, backup_obs_dir)
shutil.rmtree(temp_obs_dir)
backup_record_dir = f"/home/cloudsky/Research/Apollo/Backup/scenoRITA/records/{date.today()}"
shutil.copytree(APOLLO_RECORDS_DIR, backup_record_dir)