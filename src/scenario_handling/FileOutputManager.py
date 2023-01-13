import os
import pickle
import shutil
from datetime import date
from config import BACKUP_CONFIG_SAVE_DIR, MODULE_NAME, CURRENT_CONFIG_FILE_PATH, FITNESS_MODE, \
    AV_TESTING_APPROACH, DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR, APOLLO_RECORDS_DIR, PROJECT_ROOT, \
    BACKUP_RECORD_SAVE_DIR, APOLLO_ROOT


class FileOutputManager:

    def __init__(self):
        self.time_str = str(date.today())
        self.optimal_fitness = 0
        # option_obj_list, original_range_list, range_list
        self.file_init()

    def file_init(self):
        base_path = f"{PROJECT_ROOT}/data/exp_results/{AV_TESTING_APPROACH}/{self.time_str}"
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        self.violation_save_file_path = f"{base_path}/violation_results.txt"
        self.ind_fitness_save_file_path = f"{base_path}/ind_fitness.txt"
        self.option_tuning_file_path = f"{base_path}/option_tuning.txt"
        self.range_analysis_file_path = f"{base_path}/range_analysis.txt"
        self.record_mapping_file_path = f"{base_path}/record_mapping.txt"

        self.ind_list_pickle_dump_data_path = f"{base_path}/ind_list_pickle_pop"

        with open(self.violation_save_file_path, "w") as f:
            print()
        with open(self.ind_fitness_save_file_path, "w") as f:
            print()
        with open(self.option_tuning_file_path, "w") as f:
            print()
        with open(self.range_analysis_file_path, "w") as f:
            print()
        with open(self.record_mapping_file_path, "w") as f:
            print()

        self.delete_dir(dir_path=DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR, mk_dir=False)
        self.backup_record_file_save_path = f"{BACKUP_RECORD_SAVE_DIR}/{self.time_str}"
        self.delete_dir(dir_path=self.backup_record_file_save_path, mk_dir=True)
        self.config_file_save_path = f"{BACKUP_CONFIG_SAVE_DIR}/{self.time_str}"
        self.delete_dir(dir_path=self.config_file_save_path, mk_dir=True)


    def delete_data_core(self):
        try:
            shutil.rmtree(f"{APOLLO_ROOT}/data/core")
            os.mkdir(f"{APOLLO_ROOT}/data/core")
        except OSError as ose:
            print(ose)

    def delete_dir(self, dir_path, mk_dir):
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        if mk_dir:
            os.mkdir(dir_path)

    def save_config_file(self, gen_ind_id):
        shutil.copy(CURRENT_CONFIG_FILE_PATH, f"{self.config_file_save_path}/{gen_ind_id}/{MODULE_NAME}_config.pb.txt")

    def print_violation_results(self, generated_individual):
        print(f" Vio Results: {[len(item) for item in generated_individual.violation_results_list]}")
        print(f" Vio Emerged Num: {generated_individual.violation_intro}")
        print(f" Vio Emerged Results: {generated_individual.violations_emerged_results}")


    def save_default_scenarios(self):
        shutil.copytree(APOLLO_RECORDS_DIR, DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR)

    def handle_scenario_record(self, scenario_list):
        for scenario in scenario_list:
            if scenario.has_emerged_violations:
                scenario.save_record(self.backup_record_file_save_path)
            else:
                scenario.delete_record()

    def save_fitness_result(self, individual, gen_ind_id):
        with open(self.ind_fitness_save_file_path, "a") as f:
            f.write(f"{gen_ind_id}\n")
            f.write(f"  Vio Intro: {individual.violation_intro}\n")
            f.write(f"  Vio Remov: {individual.violation_remov}\n")
            f.write(f"  Fitness(mode: {FITNESS_MODE}): {individual.fitness}\n")
        if individual.fitness > self.optimal_fitness:
            self.optimal_fitness = individual.fitness

    def save_violation_results(self, generated_individual, scenario_list):
        for i in range(len(scenario_list)):
            violation_results = generated_individual.violation_results_list[i]
            if len(violation_results) > 0:
                with open(self.violation_save_file_path, "a") as f:
                    f.write(f"Record: {scenario_list[i].record_name}\n")
                    f.write(f"  Violation Results: {violation_results}\n")

    def output_initial_record2default_mapping(self, pre_record_info, name_prefix):
        record_name_list = [f"{name_prefix}_Scenario_{str(i)}" for i in range(pre_record_info.count)]
        for i in range(pre_record_info.count):
            with open(self.record_mapping_file_path, "a") as f:
                f.write(f"{pre_record_info.scenario_record_file_list[i]} ------ {record_name_list[i]}\n")

    def update_range_analysis_file(self, config_file_obj, range_analyzer, generation_num):
        option_obj_list = config_file_obj.option_obj_list
        with open(self.range_analysis_file_path, "w") as f:
            diff_count = 0
            f.write(f"Generation: {generation_num}\n\n")
            for i in range(len(option_obj_list)):
                if range_analyzer.original_range_list[i] != range_analyzer.range_list[i]:
                    diff_count += 1
                f.write(
                    f"Option (default): {option_obj_list[i].option_id}, {option_obj_list[i].option_type}, {option_obj_list[i].option_key}, {option_obj_list[i].option_value}\n")
                f.write(f"  Range: {range_analyzer.range_list[i]}\n")
            f.write(f"  Num of changed ranges: {diff_count}\n")

    def report_tuning_situation(self, generated_individual, config_file_obj):
        option_tuning_str = ""
        print("Report Tuning...")
        for i in range(len(config_file_obj.default_option_value_list)):
            if generated_individual.value_list[i] != config_file_obj.default_option_value_list[i]:
                option_obj = config_file_obj.option_obj_list[i]
                option_tuning_str += f"    {option_obj.option_id}, {option_obj.option_key}, {config_file_obj.default_option_value_list[i]}->{generated_individual.value_list[i]}\n"
        print(option_tuning_str)
        self.option_tuning_str = option_tuning_str

    def save_option_tuning_file(self, generated_individual, gen_ind_id, option_tuning_item, range_change_str):
        with open(self.option_tuning_file_path, "a") as f:
            f.write(f"{gen_ind_id}\n")
            f.write(f"  Total Option Tuning:\n{self.option_tuning_str}")
            f.write(f"  Current Option Tuning: {option_tuning_item}\n")
            f.write(f"  Violation Emergence Num: {len(generated_individual.violations_emerged_results)}\n")
            f.write(f"  Violation: {generated_individual.violations_emerged_results}\n")
            f.write(range_change_str)

    def save_individual_by_pickle(self, ind_list):
        ind_list.sort(reverse=True, key=lambda x: x.fitness)
        with open(self.ind_list_pickle_dump_data_path, 'wb') as f:
            pickle.dump(ind_list, f, protocol=4)

