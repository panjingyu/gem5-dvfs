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
        op_opcode = op_match.group(0)
        op_info_splitted = op_info.split()
        if len(op_info_splitted) == 1: # without operand
            op_varcode = op_opcode
        elif '[' in op_info: # operand includes any indirect addressing
            op_varcode = op_opcode + "+ia"
        # elif len()
        else:
            op_varcode = op_opcode
            # ASR, LSL, LSR, ROR, and RRX are regarded as imm
            def has_extended_imm(operand):
                return    "ASR" in op_info_splitted[i] \
                       or "LSL" in op_info_splitted[i] \
                       or "LSR" in op_info_splitted[i] \
                       or "ROR" in op_info_splitted[i] \
                       or "RRX" in op_info_splitted[i]
            for i in range(1, len(op_info_splitted)):
                if '#' in op_info_splitted[i]:
                    # direct imm
                    op_varcode = op_varcode + "+i"
                elif has_extended_imm(op_info_splitted[i]):
                    # extended imm
                    op_varcode = op_varcode + "+i"
                    break
                else:
                    # must be reg
                    op_varcode = op_varcode + "+r"
        return op_varcode
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
            if "@main " in l: # space at the tail is necessary
                assert main_block_num == 0
                main_block_num = len(op_num_blocks)
            elif "@exit_mark " in l:
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
op_blocks_main_part = op_num_blocks[main_block_num+1:exit_block_num]
eq_num = len(op_blocks_main_part)
op_num_main_part = {}
for b in op_blocks_main_part:
    for op in b:
        if op not in op_num_main_part:
            op_num_main_part[op] = 1
        else:
            op_num_main_part[op] += 1
A = np.zeros((eq_num, len(op_num_main_part)), dtype=np.int)
for i, eq_block in enumerate(op_blocks_main_part):
    # for each row of equations
    for j, k in enumerate(op_num_main_part):
        if k in eq_block:
            # nontrivial item
            A[i, j] = eq_block[k]

####### ENERGY SOLVING #######
assert len(plist) == len(clist) and len(plist) == num_stats_blocks
b_energy = (np.asarray(plist) * np.asarray(clist))[main_block_num+1:exit_block_num]
# A_with_cycles = np.c_[A, np.asarray(clist[main_block_num+1:exit_block_num]).T]
# x_e, residuals_e, rank_e, s_e = np.linalg.lstsq(A_with_cycles, b_energy, rcond=None) # op variables include cycles
x_e, residuals_e, rank_e, s_e = np.linalg.lstsq(A, b_energy, rcond=None) # cycles not included
print("main block num:{}".format(main_block_num))
print("exit block num:{}".format(exit_block_num))
print("effective eq num:{}".format(len(b_energy))) 
print("rank of A:{}".format(rank_e))
op_energy = {}
for i, k in enumerate(op_num_main_part):
    op_energy[k] = x_e[i]
# op_energy["cycle"] = x_e[-1]
sorted_op_energy = {k: v for k, v in sorted(op_energy.items(), key=lambda item: item[1]) if v}
print(sorted_op_energy)


####### CYCLE SOLVING #######
b_cycles = np.asarray(clist[main_block_num+1:exit_block_num])
x_c, residuals_c, rank_c, s_c = np.linalg.lstsq(A, b_cycles, rcond=None)
print("effective eq num:{}".format(len(b_cycles)))
print("rank of A:{}".format(rank_c))
op_cycle = {}
for i, k in enumerate(op_num_main_part):
    op_cycle[k] = x_c[i]
sorted_op_cycle = {k: v for k, v in sorted(op_cycle.items(), key=lambda item: item[1]) if v}
print(sorted_op_cycle)

####### POWER SOLUTION ########
op_power = {}
for op in op_cycle:
    op_power[op] = op_energy[op] / op_cycle[op]
sorted_op_power = {k: v for k, v in sorted(op_power.items(), key=lambda item: item[1]) if v}
print(sorted_op_power)
