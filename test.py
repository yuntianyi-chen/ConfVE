import glob
import os
import shutil
import subprocess
from pathlib import Path

# a= Path.cwd()/"asdasfa.txt.00000"
#
# print(Path.cwd()/"asdasfa.txt")
# print(Path.cwd().joinpath("asdad"))
# print(Path.home())
# print(a.stem)
# print(a.suffix)
# print(a.parent)
# print(a.suffixes)

class fff:
    def __str__(self):
        return "asdasd"
    def __repr__(self):
        return "rere"
# current_dir = Path.cwd()
# py_files = list(current_dir.glob('**/*.py'))

a = fff()

print(a.__repr__())
print(a.__str__())