import os
import re

from config import DEFAULT_CONFIG_FILE_PATH, APOLLO_ROOT
from config_file_handler.ApolloParser import ApolloParser


directory = f'{APOLLO_ROOT}/modules/planning'
variable = 'your_variable'

def find_variable_in_files(directory, variable):
    # Regex pattern to find the variable
    pattern = re.compile(r'\b{}\b'.format(variable))

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file is a .cc file
            if file.endswith('.cc'):
                with open(os.path.join(root, file), 'r') as f:
                    lines = f.readlines()
                    for line_num, line in enumerate(lines, start=1):
                        # If the variable is found in the line, print the line
                        if pattern.search(line):
                            print(f'In file {file}, line {line_num}: {line.strip()}')

# Call the function with the directory and variable name
find_variable_in_files('./', 'your_variable')





if "__name__" == "__main__":
    config_file_obj = ApolloParser.config_file_parser2obj(DEFAULT_CONFIG_FILE_PATH)

    find_variable_in_files(directory, variable)

