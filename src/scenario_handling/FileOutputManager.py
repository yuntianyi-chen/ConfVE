import os
import pickle
import shutil
from datetime import date
from config import BACKUP_CONFIG_SAVE_DIR, MODULE_NAME, CURRENT_CONFIG_FILE_PATH, FITNESS_MODE, \
    AV_TESTING_APPROACH, DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR, APOLLO_RECORDS_DIR, PROJECT_ROOT, \
    BACKUP_RECORD_SAVE_DIR, APOLLO_ROOT, MY_SCRIPTS_DIR


class FileOutputManager:

    def __init__(self):
        self.time_str = str(date.today())
        self.optimal_fitness = 0
        self.file_init()

        self.violation_type_count_dict = {}
        self.related_option_count_dict = {}
        self.scenario_violation_count_dict = {}

    def file_init(self):
        base_dir = f"{PROJECT_ROOT}/data/exp_results/{AV_TESTING_APPROACH}/{self.time_str}"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        self.violation_save_file_path = f"{base_dir}/violation_results.txt"
        self.ind_fitness_save_file_path = f"{base_dir}/ind_fitness.txt"
        self.option_tuning_file_path = f"{base_dir}/option_tuning.txt"
        self.range_analysis_file_path = f"{base_dir}/range_analysis.txt"
        self.record_mapping_file_path = f"{base_dir}/record_mapping.txt"
        self.count_dict_file_path = f"{base_dir}/count_dict.txt"
        self.vio_csv_path = f"{base_dir}/vio_csv.csv"


        self.vio_features_dir = f"{base_dir}/vio_features"
        if not os.path.exists(self.vio_features_dir):
            os.makedirs(self.vio_features_dir)



        self.ind_list_pickle_dump_data_path = f"{base_dir}/ind_list_pickle_pop"
        self.default_violation_dump_data_path = f"{base_dir}/default_violation_pickle"

        with open(self.violation_save_file_path, "w") as f:
            pass
        with open(self.ind_fitness_save_file_path, "w") as f:
            pass
        with open(self.option_tuning_file_path, "w") as f:
            pass
        with open(self.range_analysis_file_path, "w") as f:
            pass
        with open(self.record_mapping_file_path, "w") as f:
            pass
        with open(self.count_dict_file_path, "w") as f:
            pass
        with open(self.vio_csv_path, "w") as f:
            f.write("record_name,violation_type,violation_info,scenario_id,related_options\n")




        self.backup_record_file_save_path = f"{BACKUP_RECORD_SAVE_DIR}/{self.time_str}"
        self.delete_dir(dir_path=self.backup_record_file_save_path, mk_dir=True)

        self.config_file_save_path = f"{BACKUP_CONFIG_SAVE_DIR}/{self.time_str}"
        self.delete_dir(dir_path=self.config_file_save_path, mk_dir=True)

        self.move_scripts()

    def move_scripts(self):
        target_scripts_dir = MY_SCRIPTS_DIR
        if not os.path.exists(target_scripts_dir):
            source_scripts_dir = f"{PROJECT_ROOT}/data/scripts"
            shutil.copytree(source_scripts_dir, target_scripts_dir)

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
        os.mkdir(f"{self.config_file_save_path}/{gen_ind_id}")
        shutil.copy(CURRENT_CONFIG_FILE_PATH, f"{self.config_file_save_path}/{gen_ind_id}/{MODULE_NAME}_config.pb.txt")

    def save_default_scenarios(self):
        self.delete_dir(dir_path=DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR, mk_dir=False)
        shutil.copytree(APOLLO_RECORDS_DIR, DEFAULT_RERUN_INITIAL_SCENARIO_RECORD_DIR)

    def handle_scenario_record(self, scenario_list):
        for scenario in scenario_list:
            if scenario.has_emerged_violations:
                self.save_record(scenario.record_name)
                for comfirmed_record_name in scenario.confirmed_record_name_list:
                    self.save_record(comfirmed_record_name)
            else:
                self.delete_record(scenario.record_name)
                if len(scenario.confirmed_record_name_list) > 0:
                    for comfirmed_record_name in scenario.confirmed_record_name_list:
                        self.delete_record(comfirmed_record_name)

    def delete_record(self, record_name):
        os.remove(f"{APOLLO_RECORDS_DIR}/{record_name}.00000")

    def save_record(self, record_name):
        shutil.copy(f"{APOLLO_RECORDS_DIR}/{record_name}.00000",
                    f"{self.backup_record_file_save_path}/{record_name}.00000")

    def save_fitness_result(self, individual, gen_ind_id):
        with open(self.ind_fitness_save_file_path, "a") as f:
            f.write(f"{gen_ind_id}\n")
            f.write(f"  Vio Intro: {individual.violation_intro}\n")
            # f.write(f"  Vio Remov: {individual.violation_remov}\n")
            f.write(f"  Fitness(mode: {FITNESS_MODE}): {individual.fitness}\n")
        if individual.fitness > self.optimal_fitness:
            self.optimal_fitness = individual.fitness

    def print_violation_results(self, generated_individual):
        print(f" Vio Total Results: {[len(item) for item in generated_individual.violation_results_list]}")
        print(f" Vio Emerged Num: {generated_individual.violation_intro}")
        print(f" Vio Emerged Results: {[(k,v.main_type) for k,v in generated_individual.violations_emerged_results]}")

    def save_total_violation_results(self, generated_individual, scenario_list):
        with open(self.violation_save_file_path, "a") as f:
            for i in range(len(scenario_list)):
                violation_results = generated_individual.violation_results_list[i]
                if len(violation_results) > 0:
                    f.write(f"Record: {scenario_list[i].record_name}\n")
                    f.write(f"  Violation Results: {violation_results}\n\n")

    def report_tuning_situation(self, generated_individual, config_file_obj):
        self.option_tuning_id_list = []
        option_tuning_str = ""
        # print("Report Tuning...")
        for i in range(len(config_file_obj.default_option_value_list)):
            if generated_individual.value_list[i] != config_file_obj.default_option_value_list[i]:
                option_obj = config_file_obj.option_obj_list[i]
                option_tuning_str += f"    {option_obj.option_id}, {option_obj.option_key}, {config_file_obj.default_option_value_list[i]}->{generated_individual.value_list[i]}\n"

                self.option_tuning_id_list.append(option_obj.option_id)
        print(option_tuning_str)
        self.option_tuning_str = option_tuning_str

    def save_option_tuning_file(self, generated_individual, gen_ind_id, option_tuning_item, range_change_str):
        with open(self.option_tuning_file_path, "a") as f:
            f.write(f"{gen_ind_id}\n")
            f.write(f"  Total Option Tuning:\n{self.option_tuning_str}")
            f.write(f"  Current Option Tuning: {option_tuning_item}\n")
            f.write(f"  Violation Emergence Num: {len(generated_individual.violations_emerged_results)}\n")
            f.write(f"  Violation Emerged: {[(k,v.main_type) for k,v in generated_individual.violations_emerged_results]}\n")
            f.write(f"{range_change_str}\n")







    def save_vio_features(self, generated_individual, scenario_list):
        for vio_emerged_tuple in generated_individual.violations_emerged_results:
            violated_scenario_id = vio_emerged_tuple[0]
            violation_item_obj = vio_emerged_tuple[1]

            record_name = ""
            for scenario in scenario_list:
                if scenario.record_id == violated_scenario_id:
                    record_name = scenario_list[violated_scenario_id].record_name
                    break

            violation_type = violation_item_obj.main_type
            violation_features = violation_item_obj.features
            # violation_key = violation_item_obj.key_label

            self.vio_features_csv_path = f"{self.vio_features_dir}/{violation_type}_features.csv"
            if os.path.exists(self.vio_features_csv_path):
                with open(self.vio_features_csv_path, "a") as f:
                    features_values_str = ",".join(map(str,violation_features.values()))
                    f.write(f"{record_name},{violated_scenario_id},{features_values_str}\n")
            else:
                with open(self.vio_features_csv_path, "w") as f:
                    features_keys_str = ",".join(violation_features.keys())
                    f.write(f"record_name,record_id,{features_keys_str}\n")













    def save_emerged_violation_stats(self, generated_individual, scenario_list):
        # f.write("record_name, violation_type, violation_info, scenario_id, related_options")

        with open(self.vio_csv_path, "a") as f:
            for vio_emerged_tuple in generated_individual.violations_emerged_results:
                violated_scenario_id = vio_emerged_tuple[0]
                violation_item_obj = vio_emerged_tuple[1]

                record_name = scenario_list[violated_scenario_id].record_name
                violation_type = violation_item_obj.main_type
                violation_info = violation_item_obj.key_label
                scenario_id = violated_scenario_id

                related_options = ""
                for option_id in self.option_tuning_id_list:
                    related_options += f"#{option_id}" if related_options else str(option_id)

                    if option_id in self.related_option_count_dict.keys():
                        self.related_option_count_dict[option_id] += 1
                    else:
                        self.related_option_count_dict[option_id] = 1

                if violation_type in self.violation_type_count_dict.keys():
                    self.violation_type_count_dict[violation_type] += 1
                else:
                    self.violation_type_count_dict[violation_type] = 1

                if scenario_id in self.scenario_violation_count_dict.keys():
                    self.scenario_violation_count_dict[scenario_id] += 1
                else:
                    self.scenario_violation_count_dict[scenario_id] = 1

                f.write(f"{record_name},{violation_type},{violation_info},{scenario_id},{related_options}\n")

    def save_count_dict_file(self):
        with open(self.count_dict_file_path, "a") as f:
            f.write(f"Violation Type Count\n")
            f.write(f"{self.violation_type_count_dict}\n\n")
            f.write(f"----------------------------------\n")
            f.write(f"Scenario Violations Count\n")
            f.write(f"{self.scenario_violation_count_dict}\n\n")
            f.write(f"----------------------------------\n")
            f.write(f"Related Options (id: occurring time)\n")
            f.write(f"{self.related_option_count_dict}\n")

    def output_initial_record2default_mapping(self, pre_record_info_list, name_prefix):
        for pre_record_info in pre_record_info_list:
            record_name = f"{name_prefix}_Scenario_{str(pre_record_info.record_id)}"
            # record_name_list = [f"{name_prefix}_Scenario_{str(i)}" for i in range(len(pre_record_info_list))]
            with open(self.record_mapping_file_path, "a") as f:
                # for i in range(pre_record_info.count):
                f.write(f"{pre_record_info.scenario_record_file_list.record_file_path} ------ {record_name}\n")

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

    def dump_individual_by_pickle(self, ind_list):
        ind_list.sort(reverse=True, key=lambda x: x.fitness)
        with open(self.ind_list_pickle_dump_data_path, 'wb') as f:
            pickle.dump(ind_list, f, protocol=4)

    def dump_default_violation_results_by_pickle(self, default_violation_results_list):
        with open(self.default_violation_dump_data_path, 'wb') as f:
            pickle.dump(default_violation_results_list, f, protocol=4)

    def load_default_violation_results_by_pickle(self):
        default_violation_results_list = pickle.load(open(self.default_violation_dump_data_path, 'rb'))
        return default_violation_results_list


