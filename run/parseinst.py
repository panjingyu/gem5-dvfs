#!/usr/bin/env python3

import sys
import gc
import numpy as np
import op_tools

print("Start parsing insts...")

plist = op_tools.get_from_power_txt('power', 'm5out/power.txt')
clist = op_tools.get_from_power_txt('cycle', 'm5out/power.txt')

log_name = sys.argv[1]
op_priori_depth = 4 # should be near pipeline stage num
op_chain = op_tools.op_queue([], op_priori_depth)
assert len(op_chain) == 0
op_num_blocks = []
op_num_total = {}
main_block_num = exit_block_num = 0
with open(log_name, 'r') as log_file:
    log_lines = log_file.readlines()
    new_op_block_num = {}
    for l in log_lines:
        if "***** dumping stats *****" in l:
            # finish one stat block
            # add op block
            # add op number per stat block
            op_num_blocks.append(new_op_block_num)
            # add op number to total dict
            for k in new_op_block_num:
                if k in op_num_total:
                    op_num_total[k] += new_op_block_num[k]
                else:
                    op_num_total[k] = new_op_block_num[k]
            new_op_block_num = {}
        elif "system.cpu T0" in l: ##### IS micro op!!
            if "@main " in l: # space at the tail is necessary, to ensure it's the excact @main
                assert main_block_num == 0
                main_block_num = len(op_num_blocks)
            elif "@exit_mark " in l:
                assert exit_block_num == 0
                exit_block_num = len(op_num_blocks)
            op_info = l.split(":")[3] # find op info part in this gem5 log line
            op_varcode = op_tools.get_op_varcode(op_info, op_chain)
            if op_varcode not in new_op_block_num:
                new_op_block_num[op_varcode] = 1
            else:
                new_op_block_num[op_varcode] += 1
    op_num_blocks.append(new_op_block_num)

num_stats_blocks = 0
with open('m5out/stats.txt', 'r') as stats_file:
    stats_lines = stats_file.readlines()
    for l in stats_lines:
        if '---------- Begin Simulation Statistics ----------' in l:
            num_stats_blocks += 1

print("stats blocks num:{}".format(num_stats_blocks))
print("powerlist len:{}".format(len(plist)))
print("different opcode num:{}".format(len(op_num_total)))
print(len(op_num_blocks))

assert num_stats_blocks == len(op_num_blocks) or num_stats_blocks == len(op_num_blocks) - 1 # latter stands for gem5 faulty exit case
op_blocks_main_part = op_num_blocks[main_block_num+1:exit_block_num]
del op_num_blocks
gc.collect()

eq_num = len(op_blocks_main_part)
op_num_main_part = {}
for b in op_blocks_main_part:
    for op in b:
        if op not in op_num_main_part:
            op_num_main_part[op] = 1
        else:
            op_num_main_part[op] += 1
print("size of A:{}".format(eq_num * len(op_num_main_part)))
A = np.zeros((eq_num, len(op_num_main_part)), dtype=np.int)
for i, eq_block in enumerate(op_blocks_main_part):
    # for each row of equations
    for j, k in enumerate(op_num_main_part):
        if k in eq_block:
            # nontrivial item
            A[i, j] = eq_block[k]

####### ENERGY SOLVING #######
print("Start ENERGY SOLVING...")
assert len(plist) == len(clist) and len(plist) == num_stats_blocks
b_energy = (np.asarray(plist) * np.asarray(clist))[main_block_num+1:exit_block_num]
print("solving lstsq...")
x_e, residuals_e, rank_e, s_e = np.linalg.lstsq(A, b_energy, rcond=None) # cycles not included
assert exit_block_num - main_block_num - 1 == len(b_energy)
print("effective eq num:{}".format(len(b_energy))) 
print("rank of A in energy solving:{}".format(rank_e))
print("num of vars:{}".format(len(x_e)))
op_energy = {}
for i, k in enumerate(op_num_main_part):
    op_energy[k] = x_e[i]
# op_energy["cycle"] = x_e[-1]
sorted_op_energy = {k: v for k, v in sorted(op_energy.items(), key=lambda item: item[1]) if v}
# print(sorted_op_energy)
print("ENERGY SOLVING finished.")

####### CYCLE SOLVING #######
print("Start CYCLE SOLVING...")
b_cycles = np.asarray(clist[main_block_num+1:exit_block_num])
print("solving lstsq...")
x_c, residuals_c, rank_c, s_c = np.linalg.lstsq(A, b_cycles, rcond=None)
assert len(b_cycles) == len(b_energy)
print("rank of A in cycle solving:{}".format(rank_c))
print("num of vars:{}".format(len(x_c)))
op_cycle = {}
for i, k in enumerate(op_num_main_part):
    op_cycle[k] = x_c[i]
sorted_op_cycle = {k: v for k, v in sorted(op_cycle.items(), key=lambda item: item[1]) if v}
# print(sorted_op_cycle)
print("CYCLE SOLVING finished.")

####### POWER SOLUTION ########
assert len(op_energy) == len(op_cycle)
op_power = {}
for op in op_cycle:
    op_power[op] = op_energy[op] / op_cycle[op]
sorted_op_power = {k: v for k, v in sorted(op_power.items(), key=lambda item: item[1]) if v}
# print(sorted_op_power)
op_max_power = max(sorted_op_power, key=sorted_op_power.get)
print("{} by {}".format(op_max_power, sorted_op_power[op_max_power]))