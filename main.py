from optimization_algorithms.ga_main import ga_main
from container_control.container_settings import get_container_name,init_settings



if __name__ == '__main__':
    init_settings()
    ga_main()