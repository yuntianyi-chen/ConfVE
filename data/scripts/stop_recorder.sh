#!/usr/bin/env bash

###############################################################################
# Copyright 2017 The Apollo Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

cd "$(dirname "${BASH_SOURCE[0]}")"

# source "/apollo/scripts/apollo_base.sh"
python3 /apollo/scripts/record_bag.py --stop --stop_signal SIGINT
#ps -ef | grep -E 'cyber_recorder' | grep -v 'grep' | awk '{print $2}' | xargs kill -9

