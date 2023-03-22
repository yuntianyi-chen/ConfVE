import math
from typing import Tuple, Set, List

from cyber_record.record import Record
from matplotlib import pyplot as plt
from shapely.geometry import LineString

from environment.MapLoader import MapLoader
from objectives.violation_number.oracles import RecordAnalyzer
from tools.utils import calculate_velocity, extract_main_decision


def get_accel_value(message) -> float:
    accel_x = message.pose.linear_acceleration.x
    accel_y = message.pose.linear_acceleration.y
    accel_z = message.pose.linear_acceleration.z

    accel_value = math.sqrt(accel_x ** 2 + accel_y ** 2 + accel_z ** 2)
    return accel_value


def measure_violation(record_file_path):
    # ra = RecordAnalyzer(record_file_path)
    # violation_results = ra.analyze()
    accel_list = []
    velocity_list = []
    prev_ = None
    next_ = None

    record = Record(record_file_path)
    for topic, message, t in record.read_messages():
        if topic == '/apollo/localization/pose':
            if prev_ is None and next_ is None:
                prev_ = message
                continue
            next_ = message

            accel_value = get_accel_value(message)

            prev_velocity = calculate_velocity(prev_.pose.linear_velocity)
            next_velocity = calculate_velocity(next_.pose.linear_velocity)
            direction = next_velocity - prev_velocity

            if direction < 0:
                accel = accel_value * -1
            else:
                accel = accel_value

            accel_list.append(accel)
            velocity_list.append(prev_velocity)
            prev_ = message

    return accel_list, velocity_list
    # accel_list = [acc for acc in accel_list if not math.isnan(acc)]
    # plt.plot(accel_list)
    # plt.plot(velocity_list)


def analyze_acc_speed():
    dir_path = "/home/cloudsky/Research/Apollo/Backup/useful_cases"
    record_file_path = f"{dir_path}/default_Scenario_5_rerun_6.00000"
    # record_file_path = f"{dir_path}/00000005.00000"

    default_record_path = f"{dir_path}/Init_Config_6_Scenario_5.00000"
    accel_list, velocity_list = measure_violation(record_file_path)
    de_accel_list, de_velocity_list = measure_violation(default_record_path)

    fig, ax = plt.subplots()
    ax.plot(accel_list, label='Acceleration')
    ax.plot(velocity_list, label='Velocity')

    ax.plot(de_accel_list[380:], ':', label='Default Acceleration')
    ax.plot(de_velocity_list[380:], ':', label='Default Velocity')

    legend = ax.legend(shadow=True)

    plt.show()


def analyze_messages():
    dir_path = "/home/cloudsky/Research/Apollo/Backup/useful_cases"
    record_file_path = f"{dir_path}/default_Scenario_5_rerun_6.00000"


if __name__ == "__main__":
    map_instance = MapLoader().map_instance
    # analyze_acc_speed()
    analyze_messages()
