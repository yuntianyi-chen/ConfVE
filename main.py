import shutil
from datetime import date
from config import MODULE_NAME, APOLLO_ROOT, MAGGIE_ROOT, OPT_MODE, APOLLO_RECORDS_DIR
from environment.container_settings import init_settings
from optimization_algorithms.drl_main import drl_main
from optimization_algorithms.ga_main import ga_main


def select_module():
    module_config_path = f"{MAGGIE_ROOT}/data/config_files/{MODULE_NAME}/conf/{MODULE_NAME}_config.pb.txt"
    return module_config_path


if __name__ == '__main__':
    init_settings()
    module_config_path = select_module()

    if OPT_MODE =="GA":
        ga_main(module_config_path)
    elif OPT_MODE =="DRL":
        drl_main(module_config_path)

    backup_record_dir = f"/home/cloudsky/Research/Apollo/Backup/my_records/{OPT_MODE}/{date.today()}"
    shutil.copytree(APOLLO_RECORDS_DIR, backup_record_dir)