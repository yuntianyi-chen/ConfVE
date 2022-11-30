from datetime import date
from os import listdir

from config import APOLLO_ROOT, MAX_RECORD_TIME, MAGGIE_ROOT
from environment.container_settings import init_settings
from objectives.violation_number.oracles import RecordAnalyzer


def measure_objectives_individually(scenario):
    record_path = f"{APOLLO_ROOT}/records/{scenario.record_name}.00000"
    violation_results = measure_violation_number(record_path)
    # replay_scenario(record_path)
    code_coverage = measure_code_coverage()
    execution_time = measure_execution_time()
    return violation_results, code_coverage, execution_time


def measure_code_coverage():
    return 1


def measure_execution_time():
    return 1
    # return MAX_RECORD_TIME


# Most important
def measure_violation_number(record_path):
    ra = RecordAnalyzer(record_path)
    results = ra.analyze()
    print(f"      Violation Results: {results}")
    if len(results) > 0:
        print(f"          Record Path: {record_path}")
        with open(f"{MAGGIE_ROOT}/data/violation_results/violation_results_{date.today()}.txt", "a") as f:
            f.write(f"Violation Results: {results}\n")
            f.write(f"  {record_path}\n")
    return results


if __name__ == '__main__':
    SINGLE_TEST = False

    init_settings()

    record_dir = "/home/cloudsky/Research/Apollo/Backup/scenoRITA/records/2022-11-29"
    file_list = listdir(record_dir)
    file_list.sort()

    results=[]
    for i in file_list:
        if SINGLE_TEST == True:
            if "Generation37_Scenario19.00000" in i:
                result = measure_violation_number(f"{record_dir}/{i}")
                results.append(result)
        else:
            result = measure_violation_number(f"{record_dir}/{i}")
            results.append(result)

    stat_dict = {}
    for i in results:
        for j in i:
            if j not in stat_dict:
                stat_dict[j] = 1
            else:
                stat_dict[j] += 1
    print(stat_dict)

