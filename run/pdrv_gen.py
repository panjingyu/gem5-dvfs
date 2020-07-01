#!/usr/bin/env python3

import sys

import random
random.seed(42)

import json

import assemblygen
import op_tools

# adjust_dict = {
#     'vaddd': 'faddd',
#     'vsubd': 'fsubd',
#     'vmuld': 'fmuld',
#     'vdivd': 'fdivd',
# }
inst_dict = assemblygen.inst_dict_full

# best solution = "solution/2/64k-power.json"
solution_dir = "solution/2/64k-power.json"
solution_len = 24
repeat_times = 10

with open(solution_dir, 'r') as solution_file:
    op_power = json.loads(solution_file.readline()) # load op power as dict

op_keys = list(op_power.keys())
# max_power_op = max(op_power, key=op_power.get)
max_power_op = op_keys[random.randint(0, len(op_keys)-1)]
print("init op chain = {}".format(max_power_op))

def gen_reg(num_reg):
    return 'r'+str(random.randint(0,num_reg-1))
def gen_imm(opcode):
    return '#'+str(assemblygen.get_imm_operand(opcode))

op_vars = []
initial_op_vars = max_power_op.split("->")
op_chain = op_tools.op_queue(initial_op_vars, len(initial_op_vars))


if '--random' in sys.argv:
    solution_len *= 2
for i in range(solution_len):
    # priori of next op is in op_chain
    op_vars.append(op_chain.dequeue())
    if '--random' in sys.argv:
        next_op_max_power = True
        next_ops = op_keys[random.randint(0, len(op_keys)-1)].split("->")
    else:
        op_priori = op_chain.get_current_chain() + "->"
        next_op_max_power = None
        for k in op_keys:
            if k.find(op_priori) == 0:
                if next_op_max_power is None or op_power[k] > next_op_max_power:
                    next_op_max_power = op_power[k]
                    next_ops = k[len(op_priori):]
    # after every key searched
    if next_op_max_power is not None:
        if '--random' in sys.argv:
            next_op = next_ops[random.randint(0, len(next_ops)-1)]
            op_chain.enqueue(next_op)
        else:
            for next_op in next_ops.split("->"):
                # assert not op_chain.is_full()
                op_chain.enqueue(next_op)

# TODO: convert op vars to op lines
op_lines = []
for op_var in op_vars:
    op = op_var.split('+')
    if op[0] not in inst_dict:
        if op[0] in adjust_dict:
            op[0] = adjust_dict[op[0]]
            if '/' in op[0]:
                op_candidates = op[0].split('/')
                op[0] = op_candidates[random.randint(0, len(op_candidates)-1)]
        else:
            print(op)
            exit(0)
    assert "ia" not in op # indirect addressing not supported
    inst = None
    inst_template = inst_dict[op[0]]
    if '{}' not in inst_template: # exclude hard-wired cases like float ops
        inst = inst_template
    elif ''
    elif op[0] in ('ldr', 'str'):
        inst = inst_template.format(gen_reg(assemblygen.num_reg), '[fp, #-8]')
    else:
        is_using_imm = 'i' in op
        if len(inst_template) == len(inst_dict['mov']):
            if is_using_imm:
                inst = inst_template.format(gen_reg(assemblygen.num_reg), gen_imm(op[0]))
            else:
                inst = inst_template.format(gen_reg(assemblygen.num_reg), gen_reg(assemblygen.num_reg))
        elif len(inst_template) == len(inst_dict['add']):
            if is_using_imm:
                inst = inst_template.format(gen_reg(assemblygen.num_reg), gen_reg(assemblygen.num_reg), gen_imm(op[0]))
            else:
                inst = inst_template.format(gen_reg(assemblygen.num_reg), gen_reg(assemblygen.num_reg), gen_reg(assemblygen.num_reg))
        else:
            print("unsupported op encountered!")
            exit(1)
    assert inst is not None
    op_lines.append(inst)

if '--random' not in sys.argv:
    nops = "    mov r0, r0\n" * solution_len
else:
    nops = []
with open('run/pdrv.s','w') as f:
    if f.writable():
        f.write(assemblygen.prologue)
        if "--pv-only" in sys.argv:
            f.writelines(op_lines)
        else:
            for i in range(repeat_times):
                f.writelines(op_lines)
                f.writelines(nops)
        f.write(assemblygen.epilogue)
