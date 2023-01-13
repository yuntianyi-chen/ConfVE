import glob
import xml.etree.ElementTree as ET
import re
import numpy as np
import pandas as pd


def judge_arg_type(value):
    if (value == 'false' or value == 'true'):
        value_type = "boolean"
    elif (re.fullmatch("-?\d+((\\.\d+)|(\d*))", value)):
        value_type = "number"
    else:
        value_type = "string"
    # value_type = type(value)
    return value_type


if __name__ == '__main__':
    config_files_path = glob.glob(
        "C:\\Projects\\Research\\Autonomous Vehicles\\autoware\\old_version\\autoware.ai-1.11.0\\ros\\src" + '/**/*.launch',
        recursive=True)
    pd_rows = []
    for config_file_path in config_files_path:
        try:
            tree = ET.parse(config_file_path)
            root = tree.getroot()
            arg_items = list(root.iter('arg'))
            option_num = len(arg_items)

            module_name = config_file_path.split('src')[1].split('\\')[1]
            file_name = config_file_path.split('\\')[-1]

            # value_entry = list(arg_item.attrib.values())
            # value_entry.append(judge_arg_type(value_entry[1]))
            pd_rows.append([module_name, file_name, config_file_path, option_num])
            # print()
        except:
            print("An exception occurred at: "+config_file_path)
        # with open('./configuration_files/Autoware/dp_planner.launch', 'rb') as f:

    rows_df = pd.DataFrame(np.array(pd_rows), columns=['module_name', 'file_name', 'file_path', 'option_number'])
    rows_df.to_csv('autoware_config_files.csv', index=False)

        # rows = []
        # for arg_item in arg_items:
        #     value_entry = list(arg_item.attrib.values())
        #     value_entry.append(judge_arg_type(value_entry[1]))
        #     rows.append(value_entry)
        # rows_df = pd.DataFrame(np.array(rows), columns=['name', 'value', 'type'])
        # rows_df.to_csv('out.csv', index=False)
