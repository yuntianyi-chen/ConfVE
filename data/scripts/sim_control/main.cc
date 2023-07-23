#include <iostream>
#include "cyber/common/global_data.h"
#include "cyber/init.h"
#include <memory>
#include "modules/dreamview/backend/map/map_service.h"
#include "modules/sim_control/sim_control.h"
#include <unistd.h>
// bazel build //modules/sim_control:sim_control_main
// bazel run //modules/sim_control:sim_control_main
// ./bazel-bin/modules/sim_control/sim_control_main

// nohup /apollo/bazel-bin/modules/sim_control/sim_control_main &
// ps -ef | grep "sim_control_main" | grep -v 'grep' | awk '{print $2}' | xargs kill -9

int main(int argc, char *argv[]) {
    apollo::cyber::Init(argv[0]);

    std::unique_ptr<apollo::dreamview::MapService> map_service_;
    std::unique_ptr<apollo::dreamview::SimControl> sim_control_;
    FLAGS_map_dir = "/apollo/modules/map/data/borregas_ave";

    map_service_.reset(new apollo::dreamview::MapService());
    sim_control_.reset(new apollo::dreamview::SimControl(map_service_.get()));

    // sim_control_->Start();

    std::cout << "SimControl" << std::endl;

    apollo::cyber::WaitForShutdown();
    return 0;
}