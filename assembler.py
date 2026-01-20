import os
import sys
import re
import string
# import symbol_table
# import opcode_table


###########################
# Files
###########################
base_dir = os.path.dirname(os.path.abspath(__file__))

# command format: python assembler.py [input_file] [output_dir]
input_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base_dir, 'input', 'SICXE_COPY.txt')
output_dir = sys.argv[2] if len(sys.argv) > 2 else base_dir

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

input_basename = os.path.splitext(os.path.basename(input_path))[0]
log_file_path = os.path.join(output_dir, f"{input_basename}_log.txt")
intermediate_file_path = os.path.join(output_dir, f"{input_basename}_intermediate.txt")
object_file_path = os.path.join(output_dir, f"{input_basename}_object.txt")

try:
    source_file = open(input_path, mode='r', encoding='utf-8')
    log_file = open(log_file_path, mode='w', encoding='utf-8')
    intermediateFile = open(intermediate_file_path, mode='w+', encoding='utf-8')
    object_file = open(object_file_path, mode='w+', encoding='utf-8') 
except FileNotFoundError:
    print(f"Error: 找不到輸入檔案 {input_path}")
    sys.exit(1)

source_file = open(input_path, mode='r', encoding='utf-8') # your input file path
log_file = open(log_file_path, mode='w', encoding='utf-8') # your log file path
intermediate_file = open(intermediate_file_path, mode='w+', encoding='utf-8')
object_file = open(object_file_path, mode='w+', encoding='utf-8')

class LogFile:
    empty = True
    @classmethod
    def write(cls, stage, line_num, msg):
        W_STAGE = 8
        W_LINE = 12
        if log_file.tell() == 0:
            header = f"{'STAGE':<{W_STAGE}} {'LOCATION':<{W_LINE}} {'DESCRIPTION'}"
            separator = "-" * 70
            log_file.write(header + "\n")
            log_file.write(separator + "\n")
        
        error_log = f"{f'Pass {stage}':<{W_STAGE}} {f'Line {line_num}':<{W_LINE}} {msg}"
        log_file.write(error_log+"\n")
        cls.empty = False

    @classmethod
    def is_empty(cls):
        return cls.empty

    def print_log():
        log_file.seek(0)
        for log in log_file:
            print(f'{log}', ended='')

# intermediate file format: LineNum, Loc, Label, Operation, Operand, Format, Opcode, BitFlag
# Format may be null, 1, 2, 3, 4
# Opcode can be null
# BitFlag can be null
class IntermediateFile:
    def write(line_num, loc_ctr, label, operation, operand, format, opcode, bit_flag):
        WIDTH = 8
        # if intermediate_file.tell() == 0:
        #     header = f"{'LINE':<{WIDTH}} {'LOC':<{WIDTH}} {'SOURCE PROGRAM':<{WIDTH*4+2}} {'FORMAT':<{WIDTH}} {'OPCODE':<{WIDTH}} {'BIT FLAG'}"
        #     separator = "-" * 70
        #     intermediate_file.write(header + "\n")
        #     intermediate_file.write(separator + "\n")

        if loc_ctr != '-----':
            loc_ctr = f'{loc_ctr:04X}'
        intermediate_line = f"{line_num:<{WIDTH}} {loc_ctr:<{WIDTH}} {label:<{WIDTH}} {operation:<{WIDTH}} {operand:<{WIDTH*2}} {format:<{WIDTH}} {opcode:<{WIDTH}} {bit_flag}"
        intermediate_file.write(intermediate_line + "\n")
    
    def print_mid():
        global line_num
        intermediate_file.seek(0)
        line_num = 1
        for line in intermediate_file:
            print(f'{line}', end='')
            line_num += 1
        print()


class ObjectFile:
    def h_record(prog_name, start_loc, prog_len):
        WIDTH = 4
        object_program = f"{prog_name} {int(start_loc):06} {prog_len:06X}"
        object_file.write('H' + ' ' + object_program + '\n')
    
    def e_record(end_loc):
        WIDTH = 4
        object_program = f"{int(end_loc, 16):06X}"
        object_file.write('E' + ' ' + object_program + '\n')
    
    def t_record(start_addr, len, content):
        if(len == 0):
            return
        content = ' '.join(content)
        object_program = f"{start_addr:06} {len:02X} {content}"
        object_file.write('T' + ' ' + object_program + '\n')

    def print_obj():
        object_file.seek(0)
        for program in object_file:
            print(f'{program}', end='')


###########################
# Define OpTable class
###########################
class OpTable:
    FORMAT_1 = ['FIX', 'FLOAT', 'HIO', 'SIO', 'TIO', 'NORM']
    FORMAT_2 = ['CLEAR', 'COMPR', 'DIVR', 'MULR', 'RMO', 'SHIFTL', 'SHIFTR', 'SUBR', 'SVC', 'TIXR', 'ADDR']
    OPTAB = {}

    @classmethod
    def build(cls):
        file_path = os.path.join(base_dir, 'opCode.txt')
        file = open(file_path, mode='r')
        cls.OPTAB = {}
        for line in file:
            if(len(line.split())) != 2: continue
            mnemonic, opcode = line.split()
            if mnemonic in cls.FORMAT_1:
                format = 1
            elif mnemonic in cls.FORMAT_2:
                format = 2
            else: format = 3
            cls.OPTAB[mnemonic] = (opcode, format)
    @classmethod
    def search(cls, input):
        if cls.OPTAB.get(input) :
            return cls.OPTAB[input][0], cls.OPTAB[input][1] 
        else:
            return -1, -1
    @classmethod
    def isMnemonic(cls, input):
        if input in cls.OPTAB:
            return True
        else:
            return False

class SymbolTable:
    SYMTAB = {'A': '0', 'X': '1', 'L': '2', 'B': '3', 'S': '4', 'T': '5', 'F': '6', 'PC': '8', 'SW': '9'}
    @classmethod
    def build(cls, label, loc_ctr):
        if label == '-----':
            return ''
        if(label in cls.SYMTAB):
            return f'Duplicate Label at {label}'
        else:
            cls.SYMTAB[label] = hex(loc_ctr)
        return ''
    
    @classmethod
    def search(cls, input):
            if cls.SYMTAB.get(input):
                return cls.SYMTAB[input]
            else:
                return -1

###########################
# Assembler Starts here
###########################
# global var
PSEUDO = ['START', 'END', 'RESW', 'RESB', 'BYTE', 'WORD', 'BASE']

# Pass 1 variable
started = False
ended = False
line_num = 0
start_loc = 0
prog_name = 'DEFAULT'
prog_len = 0
loc_ctr = 0

# Pass 2 variable
base = 0
pc = 0

def main():
    global line_num
    OpTable.build()
    # Pass 1: generate intermediate file
    while not ended:
        raw_line = source_file.readline()
        if not raw_line: break
        
        line_num += 1
        tokens = preprocess(raw_line)
        if tokens is None: continue
        else:
            classify_tokens(tokens)
    IntermediateFile.print_mid()

    # Pass 2: assemble object program
    intermediate_file.seek(0)
    gen_object_program()
    if LogFile.is_empty:
        ObjectFile.print_obj()
    else:
        LogFile.print_log()

########################################
# Pass 1
# remove comment
# generate intermediate file
#   1. intermediate file format
#       LineNum, Loc, Label, Operation, Operand, Format, Opcode, BitFlag
#       Format may be null, 1, 2, 3, 4
#       Opcode can be null
#       BitFlag can be null
#   2. don't write in intermediate file if error
########################################
def preprocess(raw_line):
    """
    1. Remove all comments in line
    2. Normalize all comma format
    3. Tokenization
    """
    line = raw_line.partition('.')[0].strip()
    if not line:
        return None
    
    line = line.replace(' ,', ',').replace(', ', ',')
    
    tokens = line.split()
    if(len(tokens) > 3):
        LogFile.write(1, line_num, 'Syntax Error: Too much variable at this line.')
        return None
    else:
        tokens = line.split(None, 2)
    return tokens

def classify_tokens(tokens):
    global started, prog_name, ended, loc_ctr, start_loc
    match len(tokens):
        case 3:
            label, operation, operand = tokens[0], tokens[1], tokens[2]
        case 2:
            label = '-----'
            operation, operand = tokens[0], tokens[1]
            pure_op = operation.lstrip('+')
            found = OpTable.isMnemonic(pure_op)
            if not (found or pure_op in PSEUDO):
                label, operation = tokens[0], tokens[1]
                operand = '-----'
        case 1:
            label = '-----'
            operation = tokens[0]
            operand = '-----'

    # Error Case
    pure_op = operation.lstrip('+')
    if not (OpTable.isMnemonic(pure_op) or pure_op in PSEUDO):
        LogFile.write(1, line_num, "Missing operation.")
    else:
        opcode, format = OpTable.search(pure_op)
        if(pure_op == 'RSUB' or format == 1) and operand != '-----':
            LogFile.write(1, line_num, f"Redundant operand({operand}) after {pure_op}.")
            return # 或根據你的邏輯 return
        if pure_op != 'RSUB' and format >= 2 and operand == '-----':
            LogFile.write(1, line_num, f"Missing operand after {pure_op}.")
            return

    if not started and pure_op != 'START':
        LogFile.write(1, line_num, "Warning: Missing START directive; program address defaults to 0000.")
        started = True
        start_loc = 0
        loc_ctr = start_loc

    match pure_op:
        case 'START':
            if started:
                LogFile.write(1, line_num, 'Multiple START directives. Ignore this one.')
                return
            else:
                started = True
                try: start_loc = int(operand, 16)
                except ValueError:
                    LogFile.write(1, line_num, "Invalid started location; default start location to 0.")
                    start_loc = 0
                prog_name = label if label != '-----' else 'DEFAULT'

            loc_ctr = start_loc
            ret_msg = SymbolTable.build(label, loc_ctr)
            if ret_msg != "":
                LogFile.write(1, line_num, retMsg)
                return
            else:
                IntermediateFile.write(line_num, '-----', label, operation, operand, '', '', '')
        case 'END':
            global prog_len
            prog_len = loc_ctr - start_loc
            ended = True
            IntermediateFile.write(line_num, loc_ctr, label, operation, operand, '', '', '')
            return
        case 'BASE':
            retMsg = SymbolTable.build(label, loc_ctr)
            if retMsg != '':
                LogFile.write(1, line_num, retMsg)
                return
            else:
                IntermediateFile.write(line_num, '-----', label, operation, operand, '', '', '')
        case 'BYTE':
            case_byte(label, operation, operand)
        case 'WORD' | 'RESW' | 'RESB':
            retMsg = SymbolTable.build(label, loc_ctr)
            if retMsg != '':
                LogFile.write(1, line_num, retMsg)
                return
            
            try: operand = int(operand)
            except ValueError:
                LogFile.write(1, line_num, f'{operation} should followed by decimal integer')
                return

            IntermediateFile.write(line_num, loc_ctr, label, operation, operand, '', '', '')
            match operation:
                case 'RESW':
                    loc_ctr += 3 * operand
                case 'RESB':
                    loc_ctr += operand
                case 'WORD':
                    loc_ctr += 3
        # Mnemonic Code
        case _:
            retMsg = SymbolTable.build(label, loc_ctr) if label != '-----' else ''
            if retMsg != '':
                LogFile.write(1, line_num, retMsg)

            if '+' in operation:
                format = 4
            flag_bits = flag_nixe(operation, operand) if format >= 3 else ''
            IntermediateFile.write(line_num, loc_ctr, label, operation, operand, format, opcode, flag_bits)
            loc_ctr += format    
    
def case_byte(label, operation, operand):
    global line_num
    global loc_ctr
    match = re.match(r"^([CXBD])'([^']*)'$", operand)
    if not match:
        LogFile.write(1, line_num, "Error: Invalid BYTE operand format")
        return
    prefix = match.group(1)
    content = match.group(2)

    if content == '':
        LogFile.write(1, line_num, "Error: Content of BYTE cannot be null")
        return
    retMsg = SymbolTable.build(label, loc_ctr)
    if retMsg != '':
        LogFile.write(1, line_num, retMsg)
        return
    elif (prefix == 'X'):
        is_hex = all(c in string.hexdigits for c in content)
        is_even = len(content) % 2 == 0
        if not is_hex: 
            LogFile.write(1, line_num, "Error: Illegal BYTE operand.")
        elif not is_even:
            LogFile.write(2, line_num, "Error: BYTE type of X should have even number content")
        else:
            IntermediateFile.write(line_num, loc_ctr, label, operation, operand, '', '', '')
            loc_ctr += (len(content)) // 2
    elif (prefix == 'C'):
        IntermediateFile.write(line_num, loc_ctr, label, operation, operand, '', '', '')
        loc_ctr += (len(content))

def flag_nixe(operation, operand):
    """
    Return 6-bit flag (n i x b p e), set b,p as 0
    """
    if operand in ['-----', '']:
        if operation == 'RSUB':
            return '110000'
        return '000000'

    n, i, x, b, p, e = 0, 0, 0, 0, 0, 0

    if '#' in operand:    # Immediate
        n, i = 0, 1
    elif '@' in operand:  # Indirect
        n, i = 1, 0
    else:                 # Simple (including Index)
        n, i = 1, 1

    if ',' in operand:
        x = 1

    if '+' in operation:
        e = 1

    flags = f"{n}{i}{x}{b}{p}{e}"
    return flags

########################################
# Pass 2
# read intermediate file
#   intermediate file format
#       loc_ctr, label, opcode/pseudo, operand, opcode, addrMode
# generate object program
########################################
def gen_object_program():
    global base
    global pc
    t_list = []
    t_start = 0
    t_len = 0

    f = intermediate_file.readlines()
    for i in range(len(f)):
        line = f[i].split()
        line_num = line[0]
        loc = line[1]
        label = line[2]
        operation = line[3]
        operand = line[4]

        object_code = ''
        disp = 0
        match operation:
            # H Record
            case 'START':
                ObjectFile.h_record(prog_name, operand, prog_len)
                continue
            # E Record
            case 'END':
                ObjectFile.t_record(t_start, t_len, t_list)
                t_list.clear()
                t_len = 0
                end_addr = SymbolTable.search(operand)
                if end_addr == -1:
                    LogFile.write(2, line_num, f"Undefined symbol: {operand}")
                else:
                    ObjectFile.e_record(end_addr)
                continue
            # T Record
            case 'RESW' | 'RESB':   # 將現在 t_lists 當中的東西全部印出來
                ObjectFile.t_record(t_start, t_len, t_list)
                t_list, t_len = [], 0
            case 'BASE':
                base = SymbolTable.search(operand)
                if base == -1:
                    LogFile.write(2, line_num, f"Undefined symbol: {operand}")
            case 'WORD':
                object_code = f"{int(operand):06X}"
            case 'BYTE':
                match = re.match(r"^([CXBD])'([^']*)'$", operand)
                prefix, content = match.group(1), match.group(2)
                if prefix == 'X':
                    object_code = content.upper()
                elif prefix == 'C':
                    object_code = content.encode('ascii').hex().upper()
            case _:
                format = line[5] if len(line) >= 6 else None
                opcode = line[6] if len(line) >= 7 else None
                nixbpe = line[7] if len(line) >= 8 else 000000
                if format == "1" or format == "2" or operation == 'RSUB': 
                    object_code = gen_object_code(opcode, operand, format, nixbpe, 0)
                else:
                    if format == "4":
                        pure_op = operand.lstrip('@#').split(',')[0].strip()
                        if pure_op.isdigit():
                            disp = int(pure_op)
                        else:
                            target = SymbolTable.search(pure_op)
                            disp = int(target, 16) if target != -1 else 0
                    else:
                        # Format 3 處理
                        pc_val = get_pc(i, f)
                        b, p, disp = flag_bp(operand, base, pc_val)
                        # 更新 nixbpe 字串中的 b, p 位元
                        temp_nix = list(nixbpe)
                        temp_nix[3], temp_nix[4] = str(b), str(p)
                        nixbpe = "".join(temp_nix)
                    object_code = gen_object_code(opcode, operand, format, nixbpe, disp)

        if object_code:
            obj_byte_len = len(object_code) // 2
            if t_len == 0:
                t_start = f"{int(loc, 16):06X}"
            elif (t_len + obj_byte_len) > 30:
                ObjectFile.t_record(t_start, t_len, t_list)
                t_list.clear()
                t_len = 0
                t_start = f"{int(loc, 16):06X}"
            t_list.append(object_code)
            t_len += obj_byte_len

def get_pc(current_index, file_lines):
    for j in range(current_index + 1, len(file_lines)):
        parts = file_lines[j].split()
        if len(parts) >= 2: 
            if parts[1] != '-----':
                return int(parts[1], 16)
    return 0

def flag_bp(operand, base, pc):
    # 嘗試 Base 相對定址前，先檢查 base 是否有效
    if base == -1:
        LogFile.write(2, line_num, "Error: Base relative addressing failed because BASE register is undefined")
        return 0, 0, 0 # 無法定址
    
    clean_operand = operand.lstrip('@#').split(',')[0].strip()
    if clean_operand.isdigit():
        return 0, 0, int(clean_operand)
    
    target_addr = SymbolTable.search(clean_operand)    
    if target_addr == '-1':
        LogFile.write([2, line_num, f"Undefined Symbol: {operand}"])
        return 0, 0, 0
    # print("ta, base, pc", target_addr, base, pc)

    target_addr = int(target_addr, 16) if isinstance(target_addr, str) else target_addr
    curr_pc = int(pc, 16) if isinstance(pc, str) else pc
    curr_base = int(base, 16) if isinstance(base, str) else base

    disp = target_addr - curr_pc
    if -2048 <= disp <= 2047:
        return 0, 1, disp

    disp = target_addr - curr_base
    if 0 <= disp <= 4095:
        return 1, 0, disp

    LogFile.write(2, line_num, f"Out of range: {operand}")
    return 0, 0, 0

def gen_object_code(opcode, operand, format, nixbpe, address_or_disp):
    if format == "1":
        return f"{opcode:02}"
    elif format == "2":
        regs = operand.split(',')
        r1 = SymbolTable.search(regs[0])
        r2 = SymbolTable.search(regs[1]) if len(regs) > 1 else '0'
        return f"{opcode:02}{r1}{r2}"
    # --- Format 3 & 4 process --- (includes RSUB)
    bits = [int(bit) for bit in nixbpe]
    first_byte = int(opcode, 16) + (bits[0] << 1) + bits[1]
    xbpe_val = (bits[2] << 3) | (bits[3] << 2) | (bits[4] << 1) | bits[5]
    if format == "3": return f"{first_byte:02X}{xbpe_val:1X}{address_or_disp & 0xFFF:03X}"
    if format == "4": return f"{first_byte:02X}{xbpe_val:1X}{address_or_disp & 0xFFFFF:05X}"
    return ''

if __name__ == '__main__':
    main()
    source_file.close()
    intermediate_file.close()
    print()