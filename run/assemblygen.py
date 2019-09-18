#!/usr/bin/python3

import re
import random
import codegen

num_loop = 3

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
    'mov':  '    mov    {},\t{}\n',
    'add':  '    add    {},\t{},\t{}\n',
    'sub':  '    sub    {},\t{},\t{}\n',
    'mul':  '    mul    {},\t{},\t{}\n',
    'lsl':  '    lsl    {},\t{},\t{}\n',
    'lsr':  '    lsr    {},\t{},\t{}\n',
    # 'asr':  '    asr    {},\t{},\t{}\n',
    'ror':  '    ror    {},\t{},\t{}\n',
    'cmp':  '    cmp    {},\t{}\n',
    'and':  '    and    {},\t{},\t{}\n',
    'orr':  '    orr    {},\t{},\t{}\n',
    'eor':  '    eor    {},\t{},\t{}\n',
    # 'ldr':  '    ldr    {},\t{}\n',
    # 'str':  '    str    {},\t{}\n',
    'push': '    push {{{0}}}\n',
    'pop':  '    pop  {{{0}}}\n',
}
oprand_size = [
    len(inst_dict['push']),
    len(inst_dict['mov']),
    len(inst_dict['add'])
]
insts = list(inst_dict.keys())
num_inst_types = len(inst_dict)


def gen_operand(opcode, oprand0, oprand1=None):
    # opcode will be used when fp insts are involved
    if oprand1 is None:
        if oprand0 >= codegen.num_reg:
            # use immediate
            oprand0 = random.randint(0, 255)
            return '#{}'.format(oprand0)
        else:
            return 'r{}'.format(oprand0)
    else:
        if oprand1 >= codegen.num_reg:
            oprand1 = random.randint(0, 255)
            return ['r{}'.format(oprand0), '#{}'.format(oprand1)]
        else:
            return ['r{}'.format(oprand0), 'r{}'.format(oprand1)]


if __name__ == "__main__":
    program_lines = []
    with open('codegen.txt', 'r') as f:
        for line in f:
            inst_code = re.findall('\d+', line)
            opcode = insts[int(inst_code[0])]
            inst = inst_dict[opcode]
            if len(inst) == oprand_size[0]:
                inst = inst.format('r'+inst_code[1])
                # print(inst.format('r'+inst_code[1]))
            elif len(inst) == oprand_size[1]:
                oprand = gen_operand(opcode, int(inst_code[2]))
                inst = inst.format('r'+inst_code[1], oprand)
            elif len(inst) == oprand_size[2]:
                [oprand0, oprand1] = gen_operand(opcode, int(inst_code[2]), \
                                                           int(inst_code[3]))
                inst = inst.format('r'+inst_code[1], oprand0, oprand1)
            else:
                print('oprand error!')
                exit()
            program_lines.append(inst)
            


    with open('newgen.s','w') as f:
        if f.writable():
            f.write(prologue)
            f.writelines(program_lines)
            f.write(epilogue)
