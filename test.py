import os
import shutil
import subprocess

from config import APOLLO_ROOT
from environment.container_settings import get_container_name

shutil.rmtree(f"{APOLLO_ROOT}/records")
os.mkdir(f"{APOLLO_ROOT}/records")