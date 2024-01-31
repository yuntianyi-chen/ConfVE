import ruamel.yaml


class AutowareTranslator:
    # @staticmethod
    # def save2file(output_file_tuple_list):
    #     # output_file_tuple_list
    #     with open(CURRENT_CONFIG_FILE_PATH, 'w') as processed_config_file:
    #         processed_config_file.writelines(output_file_tuple_list)

    @staticmethod
    def option_obj_translator(option_obj_list, tuned_id_list):
        ruamel_yaml = ruamel.yaml.YAML()
        ruamel_yaml.preserve_quotes = True

        for tuned_id in tuned_id_list:
            option_obj = option_obj_list[tuned_id]
            ruamel_yaml_config_file = option_obj.ruamel_yaml_config_file

            # ruamel_yaml_config_file['/**']['ros__parameters'][option_obj.option_key] = option_obj.option_value
            temp_value = ruamel_yaml_config_file
            for layer in option_obj.layers:
                temp_value = temp_value[layer]
            temp_value[option_obj.option_key] = option_obj.option_value

            # with open(PROJECT_ROOT + "/aba.param.yaml", 'w') as write_file:
            with open(option_obj.config_file_path, 'w') as write_file:
                ruamel_yaml.dump(ruamel_yaml_config_file, write_file)

        # return output_file_tuple_list = [(output_string_list, output_file_path), ...]
