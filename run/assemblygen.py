#!/usr/bin/python3

import os
import sys
import getopt
import re
import random

num_reg = 10
payload_size = 800000

imm_frac = 0.5 # ratio of imm to total operand1

is_using_single_inst = False
target_inst = None


prologue = \
''' .arch armv7-a
	.eabi_attribute 27, 3
	.fpu vfp
	.eabi_attribute 20, 1
	.eabi_attribute 21, 1
	.eabi_attribute 23, 3
	.eabi_attribute 24, 1
	.eabi_attribute 25, 1
	.eabi_attribute 26, 2
	.eabi_attribute 30, 6
	.eabi_attribute 18, 4
.Ltext0:
	.align	2
	.global	main
	.type	main, %function

	@ args = 0, pretend = 0, frame = 120
	@ frame_needed = 1, uses_anonymous_args = 0
.Lfloat0:
	.word   -1717986918
	.word	1070176665
	.word	1063281229
main:                                        
	str	fp, [sp, #-4]!
    add	fp, sp, #0
    sub	sp, sp, #12
	mov	r3, #0
	str	r3, [fp, #-8]
	ldr	r3, [fp, #-8]
    fldd       d7, .Lfloat0
start_mark:
'''

epilogue = \
'''
exit_mark:
    bx      lr               @ exit program
.end
'''

inst_dict = {
    # 'push': '    push   {{{0}}}\n',       ############ Tier 0
    # 'pop':  '    pop    {{{0}}}\n',
    'mov':  '    mov    {},\t{}  \n',       ############ Tier 1 -> single operand
    'cmp':  '    cmp    {},\t{}  \n',
    'ldr':  '    ldr    {},\t{}  \n',
    'str':  '    str    {},\t{}  \n',
    ## arithmetic opcodes
    'add':  '    add    {},\t{},\t{}\n',    ############ Tier 2 -> double operands
    # 'sub':  '    sub    {},\t{},\t{}\n',
    'mul':  '    mul    {},\t{},\t{}\n',
    ## bitwise shift/rotation opcodes
    # 'lsl':  '    lsl    {},\t{},\t{}\n',
    # 'lsr':  '    lsr    {},\t{},\t{}\n',
    # 'asr':  '    asr    {},\t{},\t{}\n',
    # 'ror':  '    ror    {},\t{},\t{}\n',
    ## bitwise logic opcodes
    # 'and':  '    and    {},\t{},\t{}\n',
    # 'orr':  '    orr    {},\t{},\t{}\n',
    'eor':  '    eor    {},\t{},\t{}\n',
    ## float opcodes
    'flds':     '   flds       s15, [fp, #-12] \n',
    'fsts':     '   fsts       s15, [fp, #-12] \n',
    'fcvtds':   '   fcvtds     d6, s15         \n',
    'fcvtsd':   '   fcvtsd     s15, d7         \n',
    # 'fldd':     '   fldd       d7, .Lfloat0    \n',
    'faddd':    '   faddd      d7, d6, d7      \n',
    'fsubd':    '   fsubd      d7, d6, d7      \n',
    'fmuld':    '   fmuld      d7, d6, d7      \n',
    'fdivd':    '   fdivd      d7, d6, d7      \n',
}
insts = list(inst_dict.keys())
num_inst_types = len(inst_dict)

inst_dict_full = { # contain ops perhaps not selected in assemblygen
    # 'push': '    push   {{{0}}}\n',       ############ Tier 0
    # 'pop':  '    pop    {{{0}}}\n',
    'mov':  '    mov    {},\t{}  \n',       ############ Tier 1 -> single operand
    'cmp':  '    cmp    {},\t{}  \n',
    'ldr':  '    ldr    {},\t{}  \n',
    'str':  '    str    {},\t{}  \n',
    ## arithmetic opcodes
    'add':  '    add    {},\t{},\t{}\n',    ############ Tier 2 -> double operands
    'sub':  '    sub    {},\t{},\t{}\n',
    'mul':  '    mul    {},\t{},\t{}\n',
    ## bitwise shift/rotation opcodes
    'lsl':  '    lsl    {},\t{},\t{}\n',
    'lsr':  '    lsr    {},\t{},\t{}\n',
    'asr':  '    asr    {},\t{},\t{}\n',
    'ror':  '    ror    {},\t{},\t{}\n',
    ## bitwise logic opcodes
    'and':  '    and    {},\t{},\t{}\n',
    'orr':  '    orr    {},\t{},\t{}\n',
    'eor':  '    eor    {},\t{},\t{}\n',
    ## float opcodes
    'flds':     '   flds       s15, [fp, #-12] \n',
    'fsts':     '   fsts       s15, [fp, #-12] \n',
    'fcvtds':   '   fcvtds     d6, s15         \n',
    'fcvtsd':   '   fcvtsd     s15, d7         \n',
    # 'fldd':     '   fldd       d7, .Lfloat0    \n',
    'faddd':    '   faddd      d7, d6, d7      \n',
    'fsubd':    '   fsubd      d7, d6, d7      \n',
    'fmuld':    '   fmuld      d7, d6, d7      \n',
    'fdivd':    '   fdivd      d7, d6, d7      \n',
}
insts_full = list(inst_dict_full.keys())

# note: the output imm here use the same code as its representation
# and the range of imm should be coped with in later detailed generation
def generate_inst():
    if is_using_single_inst:
        try:
            opcode = insts.index(target_inst)
        except ValueError:
            print("opcode not found!")
            exit(1)
    else: #generate opcode randomly
        opcode   = random.randint(0, num_inst_types-1)
    dest_reg = random.randint(0, num_reg-1)
    operand0  = random.randint(0, num_reg-1) # num_reg represents immediate
    if insts[opcode] in ['mul']:
        # in this case, no imm is allowed in operand1
        operand1 = random.randint(0, num_reg-1)
    else:
        operand1 = random.randint(0, round(num_reg/(1-imm_frac)))
        if operand1 > num_reg:
            operand1 = num_reg
    while operand0 == operand1:
        operand1 = random.randint(0, num_reg-1)
    return [opcode, dest_reg, operand0, operand1]

def write_program(file_to_write):
    program = []
    for i in range(payload_size):
        inst = generate_inst()
        file_to_write.write('{0[0]}, {0[1]}, {0[2]}, {0[3]};\n'.format(inst))

def get_imm_operand(opcode):
    if opcode in insts_full:
        if opcode in ('lsl', 'lsr', 'asl', 'ror'):
            return random.randint(0, 31)
        else:
            return random.randint(0, 255)
    else:
        print('opcode not found!')
        sys.exit(1)

def gen_operand(opcode, operand0, operand1=None):
    # opcode will be used when fp insts are involved
    imm_temp = '#{}'
    if opcode in ('ldr', 'str'):
        return '[fp, #-8]'
    else:
        r_temp = 'r{}'
    if operand1 is None:
        # single operand case
        if operand0 >= num_reg:
            # use immediate
            operand0 = get_imm_operand(opcode)
            return imm_temp.format(operand0)
        else:
            return r_temp.format(operand0)
    else:
        # double operand case
        if operand1 >= num_reg:
            operand1 = get_imm_operand(opcode)
            return [r_temp.format(operand0), imm_temp.format(operand1)]
        else:
            return [r_temp.format(operand0), r_temp.format(operand1)]


if __name__ == "__main__":

    seed = 42
    original_dir = os.getcwd()
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:d:i:", ["seed=", "dir=", "inst="])
    except getopt.GetoptError:
        print('Error: getopt.GetoptError')
        sys.exit(2)

    for opt, val in opts:
        if opt in ("-s", "--seed"):
            seed = int(val)
        elif opt in ("-d", "--dir"):
            os.chdir(val)
        elif opt in ("-i", "--inst"):
            target_inst = val
            is_using_single_inst = target_inst in inst_dict
    assert not (target_inst is None and is_using_single_inst)

    random.seed(seed)
    filename_code = 'encoded/' + str(seed) + ".csv"
    filename_assembly = 'assembly/' + str(seed) + '.s'

    with open(filename_code, 'w') as f:
        write_program(f)

    program_lines = []
    with open(filename_code, 'r') as f:
        for line in f:
            inst_code = re.findall('\d+', line)
            opcode = insts[int(inst_code[0])]
            inst = inst_dict[opcode]
            if 'push' in inst_dict and len(inst) == len(inst_dict['push']):
                inst = inst.format('r'+inst_code[1])
            elif 'mov' in inst_dict and len(inst) == len(inst_dict['mov']):
                operand = gen_operand(opcode, int(inst_code[2]))
                inst = inst.format('r'+inst_code[1], operand)
            elif 'add' in inst_dict and len(inst) == len(inst_dict['add']):
                [operand0, operand1] = gen_operand(opcode, int(inst_code[2]), \
                                                           int(inst_code[3]))
                inst = inst.format('r'+inst_code[1], operand0, operand1)
            elif opcode[0] == 'f':
                # float ops
                pass
            else:
                print('operand error!')
                sys.exit(1)
            program_lines.append(inst)
            
    with open(filename_assembly,'w') as f:
        if f.writable():
            f.write(prologue)
            f.writelines(program_lines)
            f.write(epilogue)

    os.chdir(original_dir)