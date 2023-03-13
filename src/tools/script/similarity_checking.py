import os
import pandas as pd

from duplicate_elimination.ViolationChecker import compare_similarity, check_emerged_violations
from environment.MapLoader import MapLoader
from scenario_handling.FileOutputManager import FileOutputManager
from scenario_handling.MessageGenerator import MessageGenerator


def raw_test():
    features = [5, 586968.2143123412, 4141246.324113242, 1.3151733424214, 0.12, 10827, 586964.9506342566,
                4141251.703949644, -1.3494890903387966, 15.77, 5]

    default_features_list = [
        [5, 586966.321151743, 4141244.2175017213, 1.3151733085001949, 0.11, 10827, 586964.9506342566, 4141251.703949644,
         -1.3494890903387966, 15.77, 5],
        [5, 586966.3247521023, 4141244.2336821244, 1.3151598064812449, 0.08, 10827, 586964.9506342566,
         4141251.703949644,
         -1.3494890903387966, 15.77, 5],
        [5, 586966.2773055646, 4141244.0488925474, 1.315089323200107, 0.14, 10827, 586964.9506342566, 4141251.703949644,
         -1.3494890903387966, 15.77, 5]
    ]

    check_similar, sim_list = compare_similarity(features, default_features_list)

    print(check_similar, sim_list)


def real_test():
    file_output_manager = FileOutputManager()
    # message_generator = MessageGenerator()

    if os.path.exists(file_output_manager.default_violation_dump_data_path):
        default_violation_results_list_with_sid = file_output_manager.load_default_violation_results_by_pickle()
        record_id = 0
        for default_result in default_violation_results_list_with_sid:
            if record_id == default_result[0]:
                default_violations_results = default_result[1]

        feature_list=["x","y","heading","speed","speed_limit","duration"]
        value_list = [586266.096110053,4141283.590686367,1.285071800006732,12.34,11.11111111111111,0.491821]
        violation_results = dict(zip(feature_list, value_list))

        default_features_list = [d.features for d in default_violations_results if
                                 d.main_type == 'SpeedingOracle']
        compare_similarity(violation_results ,default_features_list)
        # record_id_list = [i[0] for i in default_violation_results_list_with_sid]
        #
        # message_generator.get_record_info_by_record_id(record_id_list)
        #
        # message_generator.update_selected_records_violatioin_directly(default_violation_results_list_with_sid)


    return


if __name__ == "__main__":
    map_instance = MapLoader().map_instance

    real_test()