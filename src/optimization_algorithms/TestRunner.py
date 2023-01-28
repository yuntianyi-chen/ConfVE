import os
import time
from config import INITIAL_SCENARIO_RECORD_DIR, DEFAULT_CONFIG_FILE_PATH
from config_file_handler.RangeAnalyzer import RangeAnalyzer
from config_file_handler.parser_apollo import config_file_parser2obj
from scenario_handling.FileOutputManager import FileOutputManager
from scenario_handling.MessageGenerator import MessageGenerator
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.run_scenarios import check_default_running, run_scenarios


class TestRunner:
    def __init__(self, containers):
        self.individual_num = 0

        self.containers = containers
        self.scenario_rid_emergence_list = []

        self.config_file_obj = config_file_parser2obj(DEFAULT_CONFIG_FILE_PATH)
        self.range_analyzer = RangeAnalyzer(self.config_file_obj)
        self.file_output_manager = FileOutputManager()
        self.message_generator = MessageGenerator(scenario_record_dir_path=INITIAL_SCENARIO_RECORD_DIR)
        print("Initial Scenario Violation Info:")
        self.message_generator.get_record_info_by_approach()

        print("\nDefault Config Rerun - Initial Scenario Violation Info:")
        if os.path.exists(self.file_output_manager.default_violation_dump_data_path):
            default_violation_results_list = self.file_output_manager.load_default_violation_results_by_pickle()
            self.message_generator.update_selected_records_violatioin_directly(default_violation_results_list)
        else:
            default_violation_results_list = check_default_running(self.message_generator, self.config_file_obj,
                                                                   self.file_output_manager,
                                                                   self.containers)
            self.file_output_manager.dump_default_violation_results_by_pickle(default_violation_results_list)
        self.runner_time = time.time()

    def check_scenario_list_vio_emergence(self, scenario_list):
        for scenario in scenario_list:
            if not scenario.has_emerged_module_violations:
                if scenario.record_id not in self.scenario_rid_emergence_list:
                    self.scenario_rid_emergence_list.append(scenario.record_id)



    def individual_running(self, generated_individual, ind_id):
        self.file_output_manager.delete_temp_files()
        print("-------------------------------------------------")
        print(ind_id)
        self.file_output_manager.report_tuning_situation(generated_individual, self.config_file_obj)

        generated_individual.update_id(ind_id)

        scenario_list = create_scenarios(generated_individual, self.config_file_obj,
                                         self.message_generator.pre_record_info_list,
                                         name_prefix=ind_id)

        run_scenarios(generated_individual, scenario_list, self.containers)

        generated_individual.update_fitness()

        self.check_scenario_list_vio_emergence(scenario_list)
        self.file_output_manager.print_violation_results(generated_individual)
        self.file_output_manager.save_total_violation_results(generated_individual, scenario_list)
        self.file_output_manager.handle_scenario_record(scenario_list)

        if len(generated_individual.violations_emerged_results) > 0:
            if generated_individual.option_tuning_tracking_list:
                option_tuning_item = generated_individual.option_tuning_tracking_list[-1]
            else:
                option_tuning_item = "default"

            range_change_str = self.range_analyzer.range_analyze(option_tuning_item, self.config_file_obj)
            self.file_output_manager.save_config_file(ind_id)
            # self.file_output_manager.save_fitness_result(generated_individual, ind_id)
            self.file_output_manager.save_vio_features(generated_individual, scenario_list)
            self.file_output_manager.save_option_tuning_file(generated_individual, ind_id, option_tuning_item,
                                                             range_change_str)
            self.file_output_manager.save_count_dict_file()
        self.individual_num += 1
        print(f"--------Running for {(time.time() - self.runner_time)/3600} hours-----------")


    def record_replace_and_check(self):
        self.message_generator.replace_records(self.scenario_rid_emergence_list)
        _ = check_default_running(self.message_generator, self.config_file_obj, self.file_output_manager,
                                  self.containers)
        self.scenario_rid_emergence_list = []
        self.message_generator.update_total_violation_results()



