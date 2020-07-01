#!/usr/bin/env python3

import sys
import gc
import cupy as cp
import numpy as np
import json
import op_tools

print("Start parsing insts...")

log_dir = sys.argv[1]
m5out_dir = sys.argv[2]

plist = op_tools.get_from_power_txt('power', m5out_dir + "power.txt")
clist = op_tools.get_from_power_txt('cycle', m5out_dir + "power.txt")
with open(m5out_dir+'cyclelist.txt', 'w') as cyclelist_file:
    cyclelist_file.writelines([str(c)+'\n' for c in clist])
nlist, numsnlist = op_tools.get_from_noise_txt(m5out_dir+'noise.txt')
with open(m5out_dir+'noiselist.txt','w') as noiselist_file:
    noiselist_file.writelines([str(n)+'\n' for n in nlist])
with open(m5out_dir+'numsnlist.txt','w') as numsnlist_file:
    numsnlist_file.writelines([str(n)+'\n' for n in numsnlist])

op_priori_depth = 0 # should be near pipeline stage num
op_chain = op_tools.op_queue([], op_priori_depth)
assert len(op_chain) == 0
op_num_blocks = []
op_num_total = {}
main_block_num = exit_block_num = 0
with open(log_dir, 'r') as log_file:
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
            if main_block_num == 0 and \
                ("main.0 " in l or "main " in l): # space at the tail is necessary, to ensure it's the excact main.0
                main_block_num = len(op_num_blocks)
            elif exit_block_num == 0 and \
                 ("exit.0 " in l or 'user interrupt received' in l):
                assert main_block_num
                exit_block_num = len(op_num_blocks)
            op_info_splits = l.split(":")
            if '.' in op_info_splits[2]:
                # '.' in address, meaning it's a sub-microop
                continue
            op_info = op_info_splits[3] # find op info part in this gem5 log line
            op_varcode = op_tools.get_op_varcode(op_info, op_chain)
            if op_varcode not in new_op_block_num:
                new_op_block_num[op_varcode] = 1
            else:
                new_op_block_num[op_varcode] += 1
    op_num_blocks.append(new_op_block_num)

num_stats_blocks = 0
with open(m5out_dir + 'stats.txt', 'r') as stats_file:
    stats_lines = stats_file.readlines()
    for l in stats_lines:
        if '---------- Begin Simulation Statistics ----------' in l:
            num_stats_blocks += 1

# output main part ops
op_blocks_main_part = op_num_blocks[main_block_num+1:exit_block_num]
eq_num = len(op_blocks_main_part)
op_num_main_part = {}
for b in op_blocks_main_part:
    for op in b:
        if op not in op_num_main_part:
            op_num_main_part[op] = 1
        else:
            op_num_main_part[op] += 1
with open('op_main_dic.json', 'w') as op_dict_file:
    op_dict_file.write(json.dumps(op_num_main_part, indent=1))

print("start from:{}".format(main_block_num))
print("exit at:{}".format(exit_block_num))
if "--max-power-only" in sys.argv:
    if exit_block_num > main_block_num + 1:
        power_check_range = [float(x) for x in plist[main_block_num+1:exit_block_num]]
    elif exit_block_num == 0:
        power_check_range = [float(x) for x in plist[320:]]
    else:
        power_check_range = [float(plist[main_block_num]),float(plist[exit_block_num])]
        print("weak:")
    print("max power={}".format(max(power_check_range)))
    print("mean power={}".format(np.mean(power_check_range)))
    exit(0)

print("size of A:{} * {}".format(eq_num, len(op_num_main_part)))
A = cp.zeros((eq_num, len(op_num_main_part)), dtype=cp.int)
for i, eq_block in enumerate(op_blocks_main_part):
    # for each row of equations
    for j, k in enumerate(op_num_main_part):
        if k in eq_block:
            # nontrivial item
            A[i, j] = eq_block[k]

####### ENERGY SOLVING #######
print("Start ENERGY SOLVING...")
assert len(plist) == len(clist)
b_energy = (cp.asarray(plist) * cp.asarray(clist))[main_block_num+1:exit_block_num]
print("solving lstsq...")
x_e, residuals_e, rank_e, s_e = cp.linalg.lstsq(A, b_energy) # cycles not included
assert exit_block_num - main_block_num - 1 == len(b_energy)
print("rank of A in energy solving:{}".format(rank_e))
print("num of vars:{}".format(len(x_e)))
op_energy = {}
x_e_list = x_e.tolist()
for i, k in enumerate(op_num_main_part):
    op_energy[k] = x_e_list[i]
# op_energy["cycle"] = x_e[-1]
sorted_op_energy = {k: v for k, v in sorted(op_energy.items(), key=lambda item: item[1]) if v}
# print(sorted_op_energy)
print("ENERGY SOLVING finished.")

####### CYCLE SOLVING #######
print("Start CYCLE SOLVING...")
b_cycles = cp.asarray(clist[main_block_num+1:exit_block_num])
print("solving lstsq...")
x_c, residuals_c, rank_c, s_c = cp.linalg.lstsq(A, b_cycles)
assert len(b_cycles) == len(b_energy)
print("rank of A in cycle solving:{}".format(rank_c))
print("num of vars:{}".format(len(x_c)))
op_cycle = {}
x_c_list = x_c.tolist()
for i, k in enumerate(op_num_main_part):
    op_cycle[k] = x_c_list[i]
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
print("max power op is {} by {}".format(op_max_power, sorted_op_power[op_max_power]))

with open(m5out_dir + "../" +  str(len(b_cycles)//1000) + "k-power.json", "w") as power_solution_file:
    power_solution_file.write(json.dumps(sorted_op_power, indent=1))

with open(m5out_dir + "../" +  str(len(b_cycles)//1000) + "k-cycle.json", "w") as cycle_solution_file:
    cycle_solution_file.write(json.dumps(sorted_op_cycle, indent=1))