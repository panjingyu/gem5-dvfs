import re
from assemblygen import inst_dict, equiv_dict
        
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

def get_from_noise_txt(noise_txt_dir):
    nlist = []
    nums_noise = []
    with open(noise_txt_dir, 'r') as noisetxt_file:
        for l in noisetxt_file.readlines():
            if ' noise =' in l:
                nlist.append(float(re.search('\d+\.\d+', l).group()))
            elif 'nums_noise = ' in l:
                nums_noise.append(int(re.search('\d+', l).group()))
    return (nlist, nums_noise)
        
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
        
def get_op_varcode(op_info_splitted:list) -> str:
    # op_info_splitted should be a string of micro op
    op_opcode = op_info_splitted[0]
    op_varcode = op_opcode
    found_equivalent = op_opcode in inst_dict
    if not found_equivalent:
        for k in inst_dict:
            if found_equivalent:
                break
            elif k in equiv_dict:
                keys = [k] + equiv_dict[k]
            else:
                keys = [k]
            for kk in keys:
                if found_equivalent:
                    break
                elif  op_opcode.find(kk) == 0 \
                    or (op_opcode.find(kk) == 1 and op_opcode[0] == 'u'):
                    # remove condition at the tail
                    # or convert unsigned version
                    op_varcode = k
                    found_equivalent = True
    if not found_equivalent:
        op_varcode = op_opcode + '+?'
    # ASR, LSL, LSR, ROR, and RRX are regarded as imm
    else:
        expected_operand_num = inst_dict[op_varcode].count("{}")
        while expected_operand_num + 1 > len(op_info_splitted):
            op_info_splitted += ['r']
        # if op_varcode == 'mul':
        #     # print("{} -> {}".format(op_opcode, op_varcode))
        #     print(op_info_splitted)
    if len(op_info_splitted) > 1: # not without operand
        def has_extended_imm(operand):
            return    "ASR" in op_info_splitted[i] \
                or "LSL" in op_info_splitted[i] \
                or "LSR" in op_info_splitted[i] \
                or "ROR" in op_info_splitted[i] \
                or "RRX" in op_info_splitted[i]
        for i in range(1, min(4, len(op_info_splitted))):
            if '#' in op_info_splitted[i]:
                # direct imm
                op_varcode = op_varcode + "+i"
            elif has_extended_imm(op_info_splitted[i]):
                # extended imm
                op_varcode = op_varcode + "+i"
                break
            elif '[' in op_info_splitted[i]:
                op_varcode = op_varcode + "+d"
                break
            else:
                # must be reg
                op_varcode = op_varcode + "+r"
    if op_varcode == 'mul':
        print(op_info_splitted)
    return op_varcode
