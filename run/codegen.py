#!/usr/bin/python3

import random
import assemblygen

random.seed(42)

num_reg = 10
loop_size = 10

def generate_inst():
    opcode   = random.randint(0, assemblygen.num_inst_types-1)
    dest_reg = random.randint(0, num_reg-1)
    oprand0  = random.randint(0, num_reg-1) # num_reg represents immediate
    oprand1  = random.randint(0, num_reg+5)
    return [opcode, dest_reg, oprand0, oprand1]

def write_program(file_to_write):
    program = []
    for i in range(loop_size):
        inst = generate_inst()
        f.write('{0[0]}, {0[1]}, {0[2]}, {0[3]};\n'.format(inst))

if __name__ == '__main__':
    with open('codegen.txt', 'w') as f:
        write_program(f)
