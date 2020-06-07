import re
        
def get_from_power_txt(item_name, power_txt_dir):
    ret = []
    with open(power_txt_dir, 'r') as power_file:
        power_file_lines = power_file.readlines()
        if item_name == 'power':
            pattern = re.compile("(?<=power \= )-?\d+\.\d+")
            val_formatter = float
        elif item_name == 'cycle':
            pattern = re.compile("(?<=cycle \= )\d+")
            val_formatter = int
        else:
            print("item not supported!")
            exit(1)
        for l in power_file_lines:
            match = pattern.search(l)
            if match:
                ret.append(val_formatter(match.group(0)))
    return ret

class op_queue(object):

    def __init__(self, item_list:list, max_len:int):
        self.max_len = max_len
        if len(item_list) <= max_len:
            self.items = item_list
        else:
            print("max len exceeded in op_queue init!")
            exit(2)

    def __len__(self):
        return len(self.items)
    
    def is_full(self) -> bool:
        return len(self) >= self.max_len
    
    def enqueue(self, value:str, ignore_max_len:bool = False):
        if ignore_max_len or not self.is_full():
            self.items.append(value)
        else:
            print("max len exceeded in op_queue enqueue!")

    def dequeue(self):
        return self.items.pop(0)
    
    def get_current_chain(self) -> str:
        return "->".join(self.items)
    
    def chain(self, op:str) -> str:
        was_full = self.is_full()
        self.enqueue(op, ignore_max_len=True)
        ret = self.get_current_chain()
        if was_full:
            self.dequeue()
        return ret
        
op_pattern = re.compile("[a-z_]+") # find opcode
def get_op_varcode(op_info:str, op_chain:op_queue) -> str:
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
        return op_chain.chain(op_varcode)
    else:
        print("find opcode error:")
        print(op_info)
        exit(1)