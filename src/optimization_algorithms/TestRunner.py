import os
import time

from config import INITIAL_SCENARIO_RECORD_DIR, DEFAULT_CONFIG_FILE_PATH
from config_file_handler.parser_apollo import config_file_parser2obj
from environment.MapLoader import MapLoader
from range_analysis.RangeAnalyzer import RangeAnalyzer
from scenario_handling.FileOutputManager import FileOutputManager
from scenario_handling.MessageGenerator import MessageGenerator
from scenario_handling.run_scenarios import check_default_running


class TestRunner:
    def __init__(self, containers):
        MapLoader()
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
            check_default_running(self.message_generator, self.config_file_obj, self.file_output_manager,
                                  self.containers)

        self.runner_time = time.time()

    def check_scenario_list_vio_emergence(self, scenario_list):
        for scenario in scenario_list:
            if not scenario.has_emerged_module_violations:
                if scenario.record_id not in self.scenario_rid_emergence_list:
                    self.scenario_rid_emergence_list.append(scenario.record_id)