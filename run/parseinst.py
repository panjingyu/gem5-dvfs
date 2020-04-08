#!/usr/bin/env python3

import sys
import re

with open('../m5out/powerlist.txt', 'r') as powerlist:
    plist = powerlist.readlines()

plist_iter = iter(plist)
log_name = sys.argv[1]
sim_blocks = []
other_info_lines = []
with open(log_name, 'r') as log_file:
    log_lines = log_file.readlines()
    int_pattern = re.compile('\d+')
    is_new_sim_block = False
    for l in log_lines:
        try:
            if 'info: Entering event queue' in l:
                if is_new_sim_block:
                    # last block has no instruction executed
                    try:
                        power = next(plist_iter)
                    except StopIteration:
                        power = -1
                    sim_blocks.append((sim_num, "", power))
                # process this block
                sim_num_match = int_pattern.search(l)
                if sim_num_match:
                    sim_num = sim_num_match.group(0)
                    is_new_sim_block = True
                else:
                    print("simulation block number not found!")
                    exit(1)
            elif is_new_sim_block:
                is_new_sim_block = False
                try:
                    power = next(plist_iter)
                except StopIteration:
                    power = -1
                sim_blocks.append((sim_num, l, power))
            else:
                other_info_lines.append(l)
        except StopIteration:
            break

print("sim block number: {}".format(len(sim_blocks)))
print("powerlist len:{}".format(len(plist)))