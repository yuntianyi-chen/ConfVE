import glob
import os
import shutil
import subprocess
import time
from datetime import date
from pathlib import Path

from config import MAGGIE_ROOT, OBS_DIR, APOLLO_RECORDS_DIR
from testing_approaches.scenorita.interface import ScenoRITA


dest = MAGGIE_ROOT + "/data/analysis"
report_name = "mut_features.csv"
adc_route_file = "adc_route.csv"

labels = "RecordName,x_start,y_start,x_end,y_end\n"
with open(os.path.join(dest, adc_route_file), 'w') as rfile:
    rfile.write(labels)

approach_generator = ScenoRITA()
adc_route = approach_generator.adc_routing_generate()
print(adc_route)

with open(os.path.join(dest, adc_route_file), 'a+') as rfile:
    rfile.write(f"asdsadad,{adc_route}")
