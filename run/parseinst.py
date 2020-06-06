#!/usr/bin/env python3

import sys
import re
import numpy as np

# TODO: cut off loading part of stats

op_pattern = re.compile("[a-z_]+") # find opcode
def get_op_varcode(op_info):
    # op_info should be a string of micro op
    op_match = op_pattern.search(op_info)
    if op_match:
        return op_match.group(0)
    else:
        print("find opcode error:")
        print(op_info)
        exit(1)

with open('../m5out/power.txt', 'r') as power_file:
    power_file_lines = power_file.readlines()
    power_pattern = re.compile("(?<=power \= )-?\d+\.\d+")
    cycle_pattern = re.compile("(?<=cycle \= )\d+")
    plist = []
    clist = []
    for l in power_file_lines:
        power_match = power_pattern.search(l)
        if power_match:
            plist.append(float(power_match.group(0)))
            pass
        cycle_match = cycle_pattern.search(l)
        if cycle_match:
            clist.append(int(cycle_match.group(0)))
            pass

log_name = sys.argv[1]
op_blocks = []
op_num_blocks = []
op_num_total = {}
main_block_num = exit_block_num = 0
with open(log_name, 'r') as log_file:
    log_lines = log_file.readlines()
    new_op_block = []
    new_op_block_num = {}
    for l in log_lines:
        if "***** dumping stats *****" in l:
            # finish one stat block
            # add op block
            op_blocks.append(new_op_block)
            new_op_block = []
            # add op number per stat block
            op_num_blocks.append(new_op_block_num)
            # add op number to total dict
            for k in new_op_block_num:
                if k in op_num_total:
                    op_num_total[k] += new_op_block_num[k]
                else:
                    op_num_total[k] = new_op_block_num[k]
            new_op_block_num = {}
        elif "system.cpu T0" in l:
            if "@main" in l:
                assert main_block_num == 0
                main_block_num = len(op_num_blocks)
            elif "@exit_mark" in l:
                assert exit_block_num == 0
                exit_block_num = len(op_num_blocks)
            op_info = l.split(":")[3]
            op_varcode = get_op_varcode(op_info)
            new_op_block.append(op_varcode)
            if op_varcode not in new_op_block_num:
                new_op_block_num[op_varcode] = 1
            else:
                new_op_block_num[op_varcode] += 1

    op_blocks.append(new_op_block)
    op_num_blocks.append(new_op_block_num)

num_stats_blocks = 0
with open('../m5out/stats.txt', 'r') as stats_file:
    stats_lines = stats_file.readlines()
    for l in stats_lines:
        if '---------- Begin Simulation Statistics ----------' in l:
            num_stats_blocks += 1

print("stats blocks num:{}".format(num_stats_blocks))
print("powerlist len:{}".format(len(plist)))
print("op blocks num:{}".format(len(op_blocks)))
print("different opcode num:{}".format(len(op_num_total)))

with open("../m5out/op.txt", 'w') as opcode_file:
    for block in op_blocks:
        for op in block:
            opcode_file.write(op + ' ')
        opcode_file.write('\n')

assert num_stats_blocks == len(op_num_blocks)
A = np.zeros((num_stats_blocks, len(op_num_total)), dtype=np.int)
for i, eq_block in enumerate(op_num_blocks):
    # for each row of equations
    for j, k in enumerate(op_num_total):
        if k in eq_block:
            # nontrivial item
            A[i, j] = eq_block[k]
print(np.linalg.matrix_rank(A))

assert len(plist) == len(clist) and len(plist) == num_stats_blocks
b = np.asarray(plist) * np.asarray(clist)
A = np.c_[A, np.asarray(clist).T]
x, residuals, rank, s = np.linalg.lstsq(A[main_block_num:exit_block_num], b[main_block_num:exit_block_num], rcond=None)
op_energy = {}
for i, k in enumerate(op_num_total):
    op_energy[k] = x[i]
op_energy["cycle"] = x[-1]
sorted_op_energy = {k: v for k, v in sorted(op_energy.items(), key=lambda item: item[1]) if v}
print(sorted_op_energy)
 