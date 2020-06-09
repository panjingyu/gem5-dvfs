#!/usr/bin/env python3

import json

from assemblygen import inst_dict

solution_dir = "10k-solution.json"

with open(solution_dir, 'r') as solution_file:
    op_power = json.loads(solution_file.readline()) # load op power as dict

max_power_op = max(op_power, key=sorted_op_power.get)
