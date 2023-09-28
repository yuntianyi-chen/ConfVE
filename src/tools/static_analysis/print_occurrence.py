import os
import re

from config import DEFAULT_CONFIG_FILE_PATH, APOLLO_ROOT, PROJECT_ROOT
from config_file_handler.ApolloParser import ApolloParser


directory = f'{APOLLO_ROOT}/modules/planning'

# def find_variable_in_files(directory, variable):
#     # Regex pattern to find the variable
#     pattern = re.compile(r'\b{}\b'.format(variable))
#
#     # Walk through the directory
#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             # Check if the file is a .cc file
#             if file.endswith('.cc'):
#                 with open(os.path.join(root, file), 'r') as f:
#                     lines = f.readlines()
#                     for line_num, line in enumerate(lines, start=1):
#                         # If the variable is found in the line, print the line
#                         if pattern.search(line):
#                             print(f'In file {file}, line {line_num}: {line.strip()}')

def find_variable_in_files(directory, variable, output_file):
    # Regex pattern to find the variable
    pattern = re.compile(r'\b{}_?\b.*=.*'.format(variable))

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file is a .cc file
            if file.endswith('.cc'):
                with open(os.path.join(root, file), 'r') as f:
                    lines = f.readlines()
                    for line_num, line in enumerate(lines, start=1):
                        # If the variable is found in the line, write the line to output file
                        if pattern.search(line):
                            with open(output_file, 'a') as out:
                                out.write(f'In file {file}, line {line_num}: {line.strip()}\n')
                            # print(f'In file {file}, line {line_num}: {line.strip()}')



if __name__ == '__main__':
    output_file = f'{PROJECT_ROOT}/data/other/occurrence.txt'
    config_file_obj = ApolloParser.config_file_parser2obj(DEFAULT_CONFIG_FILE_PATH)
    with open(output_file, 'w') as out:
        out.write("")

    count=0
    analyzed_option_key_list = []
    for option_key, option_value, option_type in zip(config_file_obj.option_key_list, config_file_obj.default_option_value_list,config_file_obj.option_type_list):
        if option_type in ['integer', 'float', 'e_number'] and option_key not in analyzed_option_key_list:
            with open(output_file, 'a') as out:
                count+=1
                out.write(f'\n{count} {option_key} {option_value}\n')
            find_variable_in_files(directory, option_key, output_file)
            analyzed_option_key_list.append(option_key)

