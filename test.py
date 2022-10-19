import glob
import os
import shutil
import subprocess
import time
from datetime import date
from pathlib import Path

from config import MAGGIE_ROOT

start_time = time.time()

time.sleep(5)

end_time = time.time()

print("Time cost: " + str((end_time - start_time)/3600))

