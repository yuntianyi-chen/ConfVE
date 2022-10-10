import glob
import os
import shutil
import subprocess

from config import APOLLO_ROOT
from environment.container_settings import get_container_name

files = glob.glob(f'{APOLLO_ROOT}/cyber_recorder.log.INFO.*')
for file in files:
    os.remove(file)