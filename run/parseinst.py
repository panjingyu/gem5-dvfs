#!/usr/bin/env python3

import sys
import re

with open('../m5out/powerlist.txt', 'r') as powerlist:
    plist = powerlist.readlines()

plist_iter = iter(plist)
log_name = sys.argv[1]
op_blocks = []
with open(log_name, 'r') as log_file:
    log_lines = log_file.readlines()
    op_pattern = re.compile("[a-z_]+") # find opcode
    op_mark = "system.cpu T0"
    dump_mark = "***** dumping stats *****"
    new_op_block = []
    for l in log_lines:
        if dump_mark in l:
            op_blocks.append(new_op_block)
            new_op_block = []
        if op_mark in l:
            op_info = l.split(":")
            op_match = op_pattern.search(op_info[3])
            if op_match:
                op_opcode = op_match.group(0)
                new_op_block.append(op_opcode)
            else:
                print("find opcode error:")
                print(op_info)
                exit(1)
    op_blocks.append(new_op_block)

num_stats_blocks = 0
with open('../m5out/stats.txt', 'r') as stats_file:
    stats_lines = stats_file.readlines()
    for l in stats_lines:
        if '---------- Begin Simulation Statistics ----------' in l:
            num_stats_blocks += 1
            

print("stats blocks num:{}".format(num_stats_blocks))
print("powerlist len:{}".format(len(plist)))
print("op blocks num:{}".format(len(op_blocks)))

with open("../m5out/op.txt", 'w') as opcode_file:
    for block in op_blocks:
        for op in block:
            opcode_file.write(op + ' ')
        opcode_file.write('\n')