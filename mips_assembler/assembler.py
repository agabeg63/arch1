from pickle import TRUE
import sys
import os
from enum import Enum
from tempfile import TemporaryFile
import re
import ctypes
import this

from matplotlib.pyplot import text
from nbformat import write

################################################
# For debug option. If you want to debug, set 1
# If not, set 0.
################################################

DEBUG = 0

MAX_SYMBOL_TABLE_SIZE = 1024
MEM_TEXT_START = 0x00400000
MEM_DATA_START = 0x10000000
BYTES_PER_WORD = 4
INST_LIST_LEN = 27

################################################
# Additional Components
################################################

class bcolors:
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'


start = '[' + bcolors.BLUE + 'START' + bcolors.ENDC + ']  '
done = '[' + bcolors.YELLOW + 'DONE' + bcolors.ENDC + ']   '
success = '[' + bcolors.GREEN + 'SUCCESS' + bcolors.ENDC + ']'
error = '[' + bcolors.RED + 'ERROR' + bcolors.ENDC + ']  '

pType = [start, done, success, error]


def log(printType, content):
    print(pType[printType] + content)


################################################
# Structure Declaration
################################################

class inst_t:
    def __init__(self, name, op, type, funct):
        self.name = name
        self.op = op
        self.type = type
        self.funct = funct


class symbol_t:
    def __init__(self):
        self.name = 0
        self.address = 0


class la_struct:
    def __init__(self, op, rt, imm):
        self.op = op
        self.rt = rt
        self.imm = imm


class section(Enum):
    DATA = 0
    TEXT = 1
    MAX_SIZE = 2


################################################
# Global Variable Declaration
################################################

ADD = inst_t("add", "000000", 'R', "100000")
ADDI = inst_t("addi", "001000", 'I', "")
ADDIU = inst_t("addiu", "001001", 'I', "")
ADDU = inst_t("addu",    "000000", 'R', "100001")
AND = inst_t("and",     "000000", 'R', "100100")
ANDI = inst_t("andi",    "001100", 'I', "")
BEQ = inst_t("beq",     "000100", 'I', "")
BNE = inst_t("bne",     "000101", 'I', "")
J = inst_t("j",       "000010", 'J', "")
JAL = inst_t("jal",     "000011", 'J', "")
JR = inst_t("jr",      "000000", 'R', "001000")
LHU = inst_t("lhu",     "100101", 'I', "")
LUI = inst_t("lui",     "001111", 'I', "")
LW = inst_t("lw",      "100011", 'I', "")
NOR = inst_t("nor",     "000000", 'R', "100111")
OR = inst_t("or",      "000000", 'R', "100101")
ORI = inst_t("ori",     "001101", 'I', "")
SLT = inst_t("slt", "000000", 'R', "101010")
SLTI = inst_t("slti", "001010", 'I', "")
SLTIU = inst_t("sltiu",    "001011", 'I', "")
SLTU = inst_t("sltu",    "000000", 'R', "101011")
SLL = inst_t("sll",     "000000", 'R', "000000")
SRL = inst_t("srl",     "000000", 'R', "000010")
SH = inst_t("sh", "101001", 'I', "")
SW = inst_t("sw",      "101011", 'I', "")
SUB = inst_t("sub", "000000", 'R', "100010")
SUBU = inst_t("subu",    "000000", 'R', "100011")

inst_list = [ADD,  ADDI, ADDIU, ADDU, AND,
             ANDI, BEQ,  BNE,   J,    JAL, 
             JR,   LHU,  LUI,   LW,   NOR,
             OR,   ORI,  SLT,   SLTI, SLTIU,  
             SLTU, SLL,  SRL,   SH,   SW, 
             SUB,  SUBU, ]

# Global symbol table
symbol_struct = symbol_t()
SYMBOL_TABLE = [symbol_struct] * MAX_SYMBOL_TABLE_SIZE

# For indexing of symbol table
symbol_table_cur_index = 0

# Temporary file stream pointers
data_seg = None
text_seg = None

# Size of each section
data_section_size = 0
text_section_size = 0


################################################
# Function Declaration
################################################

# Change file extension from ".s" to ".o"
def change_file_ext(fin_name):
    fname_list = fin_name.split('.')
    fname_list[-1] = 'o'
    fout_name = ('.').join(fname_list)
    return fout_name

# Add symbol to global symbol table
def symbol_table_add_entry(symbol):
    global SYMBOL_TABLE
    global symbol_table_cur_index

    SYMBOL_TABLE[symbol_table_cur_index] = symbol
    symbol_table_cur_index += 1
    if DEBUG:
        print("symbol table content:\n")
        log(1, f"{symbol.name}: 0x" + hex(symbol.address)[2:].zfill(8))

# Convert integer number to binary string
def num_to_bits(num, len):
    bit = bin(num & (2**len-1))[2:].zfill(len)
    return bit

# Fill the blanks
def make_symbol_table(input):
    size_bit = 0
    address = 0
    cur_section = section.MAX_SIZE.value
    global data_section_size
    global text_section_size
    
    global text_seg
    global data_seg   
    # Read .data section
    lines = input.readlines()
    for line in lines:
        line = line.strip()
        #print("cur_section is ", cur_section)
        _line = line
        token_line = _line.strip('\n\t').split()
        temp = token_line[0]
        if temp == ".data":
            '''
            blank
            '''
            cur_section = section.DATA.value
            address = MEM_DATA_START
            data_seg = TemporaryFile('w+t')
            continue

        if temp == ".text":
            '''
            blank
            '''
            cur_section = section.TEXT.value
            address = MEM_TEXT_START
            text_seg = TemporaryFile('w+t')
            continue

        if cur_section == section.DATA.value:
            '''
            blank
            '''
            
            #print("Symbol table line : ")
            symbol_str = symbol_t()
            symbol_str.name = temp[:-1]
            #print(temp, " ")
            symbol_str.address = hex(address)
            #print(hex(address), "\n")
            symbol_table_add_entry(symbol_str)
            #print("Data segment line: ")
            data_seg.write(str(token_line[-2]))   #needs clarification
            #print(str(token_line[-2]), " ")
            data_seg.write(" ")
            data_seg.write(str(token_line[-1]))
            #print(str(token_line[-1]), "\n")
            data_seg.write("\n")
            data_section_size = data_section_size + 4
        
        elif cur_section == section.TEXT.value:
            '''
            blank
            '''
            
            exist = False
            for list in inst_list:
                if temp == list.name:
                    exist = True
            if temp == "la" or temp == "move":
                exist = True        
            if exist == False:
                temp = temp[:-1]
                symbol_str = symbol_t()
                #print("Symbol table line : ")
                symbol_str.name = temp
                #print(temp, " ")
                symbol_str.address = hex(address)
                #print(hex(address), "\n")
                symbol_table_add_entry(symbol_str)
                address = address - 4
            if exist == True:
                for index in token_line:
                    text_seg.write(str(index))
                    text_seg.write(" ")
                    #print("Text segment line: ")
                    #print(str(index), " ")
                #print("\n")
                text_seg.write("\n")
                text_section_size = text_section_size + 4
                if temp == "la":
                    for data in SYMBOL_TABLE:
                        if token_line[2] == data.name:
                            if data.address != "0x10000000":
                                text_section_size += 4
                     

        address += BYTES_PER_WORD
    print("text_section_size is : ", text_section_size)
    print("data_section_size is : ", data_section_size)

# Record .text section to output file
def record_text_section(fout):
    # print text section
    cur_addr = MEM_TEXT_START
    global text_section_size
    text_seg.seek(0)
    lines = text_seg.readlines()
    for ind in range(10):
        print("Symbol table: ", SYMBOL_TABLE[ind].name, SYMBOL_TABLE[ind].address)
    for line in lines:
        line = line.strip()
        _line = line
        token_line = _line.strip().split()
        temp = token_line[0]
        #print("content of text_seg: ")
        #print(temp)
        for index in range(1, len(token_line)):
            print(token_line[index])
        i, idx, type, rs, rt, rd, imm, shamt = 0, 0, '0', 0, 0, 0, 0, 0
        
        '''
        blank: Find the instruction type that matches the line

        '''
        funct = ""
        op = ""
        for list in inst_list:
            if(temp == list.name):
                type = list.type
                funct = list.funct
                op = list.op
                break
        
        for index in range(1, len(token_line)):
            if(token_line[index][0] == '$'):
                s = token_line[index][1:]
                token_line[index] = s
                #print("without $ ", token_line[index])

        for index in range(1, len(token_line)):
            if(token_line[index][-1] == ','):
                s = token_line[index][:-1]
                token_line[index] = s
                #print("without , ", token_line[index])
        
        if type == 'R':
            '''
            blank
            '''
            if temp == "jr":
                rs = int(token_line[1])
                rs = num_to_bits(rs, 5)
                rd = num_to_bits(0, 5)
                rt = num_to_bits(0, 5)
                shamt = num_to_bits(shamt, 5)
            elif temp == "sll" or temp == "srl":
                rt = int(token_line[2])
                rt = num_to_bits(rt, 5)
                shamt = int(token_line[3])
                shamt = num_to_bits(shamt, 5)
                rs = num_to_bits(0, 5)
                rd = num_to_bits(0, 5)
            else:
                rd = int(token_line[1])
                rd = num_to_bits(rd, 5)
                rs = int(token_line[2])
                rs = num_to_bits(rs, 5)
                rt = int(token_line[3])
                rt = num_to_bits(rt, 5)
                shamt = num_to_bits(shamt, 5)



                
            fout.write(op)
            #print("op is ", op)
            fout.write(rs)
            #print(rs)
            fout.write(rt)
            #print(rt)
            fout.write(rd)
            #print(rd)
            fout.write(shamt)
            #print(shamt)
            fout.write(funct)
            #print(funct)

            if DEBUG:
                log(1, f"0x" + hex(cur_addr)[2:].zfill(
                    8) + f": op: {op} rs:${rs} rt:${rt} rd:${rd} shamt:{shamt} funct:{inst_list[idx].funct}")

        if type == 'I':
            '''
            blank
            '''

            fout.write(op)
            if temp == "beq" or temp == "bne":
                rs = int(token_line[1])
                rs = num_to_bits(rs, 5)
                rt = int(token_line[2])
                rt = num_to_bits(rt, 5)
                for index in SYMBOL_TABLE:
                   if token_line[3] == index.name:
                        imm = int(index.address, 16)
                        imm = num_to_bits(imm, 16)
                
            elif temp != "lw" and temp != "sw" and temp != "lui" and temp != "sh" and temp != "lhu":
                rt = int(token_line[1])
                rt = num_to_bits(rt, 5)
                rs = int(token_line[2])
                rs = num_to_bits(rs, 5)
                imm = int(token_line[3], 16)
                imm = num_to_bits(imm, 16)

            elif temp == "lw" or temp =="sw" or temp =="sh" or temp =="lhu":
                rt = int(token_line[1])
                rt = num_to_bits(rt, 5)
                spl = token_line[2].strip(')')
                _spl = spl.split("($")
                #print("without ) and $ : ", _spl[0], _spl[1])
                imm = int(_spl[0])
                imm = num_to_bits(imm, 16)
                rs = int(_spl[1])
                rs = num_to_bits(rs, 5)
            elif temp == "lui": 
                rt = int(token_line[1])
                rt = num_to_bits(rt, 5)
                imm = int(token_line[2], 16)
                imm = num_to_bits(imm, 16)
                rs = num_to_bits(0, 5)
            fout.write(rs)
            fout.write(rt)
            fout.write(imm)
            if DEBUG:
                log(1, f"0x" + hex(cur_addr)
                    [2:].zfill(8) + f": op:{op} rs:${rs} rt:${rt} imm:0x{imm}")

        if type == 'J':
            '''
            blank
            '''

            fout.write(op)
            for index in SYMBOL_TABLE:
                if token_line[1] == index.name:
                    addr = int(index.address, 16)
                    addr = num_to_bits(addr, 26)
            fout.write(addr)

            if DEBUG:
                log(1, f"0x" + hex(cur_addr)
                    [2:].zfill(8) + f" op:{op} addr:{addr}")
        if token_line[0] == "la":
            addr = 0
            for index in SYMBOL_TABLE:
                if token_line[2] == index.name:
                    addr = int(index.address, 16)
                    #print("la int addr: ", addr)
        
            if num_to_bits(addr, 16) == "0000000000000000":
                #print("la is lui:")
                op = "001111"
                rt = int(token_line[1])
                rt = num_to_bits(rt, 5)
                imm = "0001000000000000"
                rs = num_to_bits(0, 5)
                fout.write(op)
                fout.write(rs)
                fout.write(rt)
                fout.write(imm)
            if(num_to_bits(addr, 16)) != "0000000000000000":
                #print("la is lui and ori:")
                op = "001111"
                rt = int(token_line[1])
                rt = num_to_bits(rt, 5)
                imm = "0001000000000000"
                rs = num_to_bits(0, 5)
                fout.write(op)
                fout.write(rs)
                fout.write(rt)
                fout.write(imm)
                fout.write("\n")
                op = "001101"
                rt = int(token_line[1])
                rt = num_to_bits(rt, 5)
                rs = rt
                imm = num_to_bits(addr, 16)
                fout.write(op)
                fout.write(rs)
                fout.write(rt)
                fout.write(imm)
                text_section_size += 4
        if token_line[0] == "move":
            op = "000000"
            rd = int(token_line[1])
            rd = num_to_bits(rd, 5)
            rs = int(token_line[2])
            rs = num_to_bits(rs, 5)
            rt = num_to_bits(0, 5)
            shamt = num_to_bits(0, 5)
            funct = "100000"
            fout.write(op)
            fout.write(rs)
            fout.write(rt)
            fout.write(rd)
            fout.write(shamt)
            fout.write(funct)
                


        fout.write("\n")
        cur_addr += BYTES_PER_WORD
    

# Record .data section to output file
def record_data_section(fout):
    cur_addr = MEM_DATA_START
    data_seg.seek(0)

    lines = data_seg.readlines()
    for line in lines:
        '''
        blank
        '''
        line = line.strip()
        _line = line
        token_line = _line.strip().split()
        temp = token_line[1]
        print("this is data segment: ", temp)
        if temp[0] == '0':
            num = int(temp, 16)
        else:
            num = int(temp)

        number = num_to_bits(num, 32)
        fout.write(number)
        fout.write("\n")

        if DEBUG:
            log(1, f"0x" + hex(cur_addr)[2:].zfill(8) + f": {line}")

        cur_addr += BYTES_PER_WORD

# Fill the blanks
def make_binary_file(fout):
    if DEBUG:
        # print assembly code of text section
        text_seg.seek(0)
        lines = text_seg.readlines()
        for line in lines:
            line = line.strip()

    # print text_size, data_size
    if DEBUG:
        log(1,
            f"text size: {text_section_size}, data size: {data_section_size}")

    '''
    blank: Print text section size and data section size
    '''

    binary_text = num_to_bits(text_section_size, 32)
    fout.write(binary_text)
    fout.write("\n")
    binary_data = num_to_bits(data_section_size,32)
    fout.write(binary_data)
    fout.write("\n")
    record_text_section(fout)
    record_data_section(fout)
    





################################################
# Function: main
#
# Parameters:
#   argc: the number of argument
#   argv[]: the array of a string argument
#
# Return:
#   return success exit value
#
# Info:
#   The typical main function in Python language.
#   It reads system arguments from terminal (or commands)
#   and parse an assembly file(*.s)
#   Then, it converts a certain instruction into
#   object code which is basically binary code
################################################


if __name__ == '__main__':
    argc = len(sys.argv)
    log(1, f"Arguments count: {argc}")

    if argc != 2:
        log(3, f"Usage   : {sys.argv[0]} <*.s>")
        log(3, f"Example : {sys.argv[0]} sample_input/example.s")
        exit(1)

    input_filename = sys.argv[1]
    input_filePath = os.path.join(os.curdir, input_filename)

    if os.path.exists(input_filePath) == False:
        log(3,
            f"No input file {input_filename} exists. Please check the file name and path.")
        exit(1)

    f_in = open(input_filePath, 'r')

    if f_in == None:
        log(3,
            f"Input file {input_filename} is not opened. Please check the file")
        exit(1)

    output_filename = change_file_ext(sys.argv[1])
    output_filePath = os.path.join(os.curdir, output_filename)

    if os.path.exists(output_filePath) == True:
        log(0, f"Output file {output_filename} exists. Remake the file")
        os.remove(output_filePath)
    else:
        log(0, f"Output file {output_filename} does not exist. Make the file")

    f_out = open(output_filePath, 'w')
    if f_out == None:
        log(3,
            f"Output file {output_filename} is not opened. Please check the file")
        exit(1)

    ################################################
    # Let's compelte the below functions!
    #
    #   make_symbol_table(input)
    #   make_binary_file(output)
    ################################################

    make_symbol_table(f_in)
    make_binary_file(f_out)

    text_seg.close()
    data_seg.close()

    f_in.close()
    f_out.close()
