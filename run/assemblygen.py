#!/usr/bin/python3

import os
import sys
import getopt
import re
import random

num_loop = 3
num_reg = 10
loop_size = 12

prologue = \
'''.Ltext0:
    .align	2
    .global	main
    .type	main, %function
    .equ    num_loop, ''' + str(num_loop) + \
'''
main:                                        
    mov     r12, #0 @ r12 = 0
loop:
'''

epilogue = \
'''
    add     r12, r12, #1     @ Add 1 to r12
test_loop:
    cmp     r12, #num_loop   @ for loop condition
    blt     loop
.end
'''

inst_dict = {
    'push': '    push   {{{0}}}\n',
    'pop':  '    pop    {{{0}}}\n',
    'mov':  '    mov    {},\t{}  \n',
    'cmp':  '    cmp    {},\t{}  \n',
    # 'ldr':  '    ldr    {},\t{}  \n',
    # 'str':  '    str    {},\t{}  \n',
    ## arithmetic opcodes
    'add':  '    add    {},\t{},\t{}\n',
    'sub':  '    sub    {},\t{},\t{}\n',
    'mul':  '    mul    {},\t{},\t{}\n',
    # 'div':  '    div    {},\t{},\t{}\n',
    ## bitwise shift/rotation opcodes
    'lsl':  '    lsl    {},\t{},\t{}\n',
    'lsr':  '    lsr    {},\t{},\t{}\n',
    # 'asr':  '    asr    {},\t{},\t{}\n',
    'ror':  '    ror    {},\t{},\t{}\n',
    ## bitwise logic opcodes
    'and':  '    and    {},\t{},\t{}\n',
    'orr':  '    orr    {},\t{},\t{}\n',
    'eor':  '    eor    {},\t{},\t{}\n',
}
oprand_size = [
    len(inst_dict['push']),
    len(inst_dict['mov']),
    len(inst_dict['add'])
]
insts = list(inst_dict.keys())
num_inst_types = len(inst_dict)

# note: the output imm here use the same code as its representation
# and the range of imm should be coped with in later detailed generation
def generate_inst():
    imm_frac = 0.2 # ratio of imm to total oprand1
    opcode   = random.randint(0, num_inst_types-1)
    dest_reg = random.randint(0, num_reg-1)
    oprand0  = random.randint(0, num_reg-1) # num_reg represents immediate
    if insts[opcode] in ['mul']:
        # in this case, no imm is allowed in oprand1
        oprand1 = random.randint(0, num_reg-1)
    else:
        oprand1 = random.randint(0, round(num_reg/(1-imm_frac)))
        if oprand1 > num_reg:
            oprand1 = num_reg
    return [opcode, dest_reg, oprand0, oprand1]

def write_program(file_to_write):
    program = []
    for i in range(loop_size):
        inst = generate_inst()
        f.write('{0[0]}, {0[1]}, {0[2]}, {0[3]};\n'.format(inst))

def get_imm_oprand(opcode):
    if opcode in inst:
        if opcode in ('lsl', 'lsr', 'asl', 'ror'):
            return random.randint(0, 32)
        else:
            return random.randint(0, 255)
    else:
        print('opcode not found!')
        sys.exit(1)

def gen_operand(opcode, oprand0, oprand1=None):
    # opcode will be used when fp insts are involved
    if oprand1 is None:
        # single oprand case
        if oprand0 >= num_reg:
            # use immediate
            oprand0 = get_imm_oprand(opcode)
            return '#{}'.format(oprand0)
        else:
            return 'r{}'.format(oprand0)
    else:
        # double oprand case
        if oprand1 >= num_reg:
            oprand1 = get_imm_oprand(opcode)
            return ['r{}'.format(oprand0), '#{}'.format(oprand1)]
        else:
            return ['r{}'.format(oprand0), 'r{}'.format(oprand1)]


if __name__ == "__main__":

    seed = 42
    original_dir = os.getcwd()
    
    try:
        opts, args = getopt.getopt(argv, "s:d:", ["seed", "dir"])
    except getopt.GetoptError:
        print('Error: getopt.GetoptError')
        sys.exit(2)

    for opt, val in opts:
        if opt in ("-s", "--seed"):
            seed = int(val)
        elif opt in ("-d", "--dir"):
            os.chdir(val)


    random.seed(seed)
    filename_code = seed + ".txt"
    filename_assembly = seed + '.s'

    with open(filename_code, 'w') as f:
        write_program(f)

    program_lines = []
    with open(filename_code, 'r') as f:
        for line in f:
            inst_code = re.findall('\d+', line)
            opcode = insts[int(inst_code[0])]
            inst = inst_dict[opcode]
            if len(inst) == oprand_size[0]:
                inst = inst.format('r'+inst_code[1])
            elif len(inst) == oprand_size[1]:
                oprand = gen_operand(opcode, int(inst_code[2]))
                inst = inst.format('r'+inst_code[1], oprand)
            elif len(inst) == oprand_size[2]:
                [oprand0, oprand1] = gen_operand(opcode, int(inst_code[2]), \
                                                         int(inst_code[3]))
                inst = inst.format('r'+inst_code[1], oprand0, oprand1)
            else:
                print('oprand error!')
                sys.exit(1)
            program_lines.append(inst)
            
    with open(filename_assembly,'w') as f:
        if f.writable():
            f.write(prologue)
            f.writelines(program_lines)
            f.write(epilogue)

    os.chdir(original_dir)