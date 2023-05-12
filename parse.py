'''
MIPS-32 Instruction Level Simulatr

CSE261 UNIST
parse.py
'''

from sklearn.neighbors import VALID_METRICS
from run import SET_FUNC, SET_IMM, SET_OPCODE, SET_RD, SET_RS, SET_RT, SET_SHAMT, SET_TARGET
from util import fromBinary
import util
import initialize
import ctypes


def parse_instr(buffer, index):
    instr = util.instruction()
    value_int = fromBinary(buffer)
    instr.value = value_int
    
    opcode_int = fromBinary(buffer[:6])
    SET_OPCODE(instr, opcode_int)
    if instr.opcode == 0x0:
          # this is R type
          rs_int = fromBinary(buffer[6:11])
          SET_RS(instr, rs_int)
          rt_int = fromBinary(buffer[11:16])
          SET_RT(instr, rt_int)
          rd_int = fromBinary(buffer[16:21])
          SET_RD(instr, rd_int)
          shamt_int = fromBinary(buffer[21:26])
          SET_SHAMT(instr,shamt_int)
          func_int = fromBinary(buffer[26:32])
          SET_FUNC(instr, func_int)
    elif instr.opcode == 0x8 or instr.opcode == 0x9 \
                or instr.opcode == 0xc or instr.opcode == 0x4 \
                or instr.opcode == 0x5 or instr.opcode == 0x25 \
                or instr.opcode == 0xf or instr.opcode == 0x23 \
                or instr.opcode == 0xd or instr.opcode == 0xa \
                or instr.opcode == 0xb or instr.opcode == 0x29 \
                or instr.opcode == 0x2b:
          # this is I types
          rs_int = fromBinary(buffer[6:11])
          SET_RS(instr, rs_int)
          rt_int = fromBinary(buffer[11:16])
          SET_RT(instr, rt_int)
          rt_imm = fromBinary(buffer[16:32])
          SET_IMM(instr, rt_imm)
    elif instr.opcode == 0x2 or instr.opcode == 0x3:
          # this is J type
          target_int = fromBinary(buffer[6:32])
          SET_TARGET(instr, target_int)

    # Implement this function
    

    return instr

def parse_data(buffer, index):
    # Implement this function
    buffer_int = fromBinary(buffer)
    util.mem_write(index + util.MEM_DATA_START, buffer_int)
    # erase "pass" to start implementing
      

def print_parse_result(INST_INFO):
    print("Instruction Information")

    for i in range(initialize.text_size//4):
        print("INST_INFO[", i, "].value : ", "%8x" % INST_INFO[i].value)
        print("INST_INFO[", i, "].opcode : ", INST_INFO[i].opcode)

        # TYPE I
        # 0x8: (0x001000)ADDI
        # 0x9: (0x001001)ADDIU
        # 0xc: (0x001100)ANDI
        # 0x4: (0x000100)BEQ
        # 0x5: (0x000101)BNE
        # 0x25: (0x011001)LHU
        # 0xf: (0x001111)LUI
        # 0x23: (0x100011)LW
        # 0xd: (0x001101)ORI
        # 0xa: (0x001010)SLTI
        # 0xb: (0x001011)SLTIU
        # 0x29: (0x011101)SH
        # 0x2b: (0x101011)SW

        if INST_INFO[i].opcode == 0x8 or INST_INFO[i].opcode == 0x9 \
                or INST_INFO[i].opcode == 0xc or INST_INFO[i].opcode == 0x4 \
                or INST_INFO[i].opcode == 0x5 or INST_INFO[i].opcode == 0x25 \
                or INST_INFO[i].opcode == 0xf or INST_INFO[i].opcode == 0x23 \
                or INST_INFO[i].opcode == 0xd or INST_INFO[i].opcode == 0xa \
                or INST_INFO[i].opcode == 0xb or INST_INFO[i].opcode == 0x29 \
                or INST_INFO[i].opcode == 0x2b:
            print("INST_INFO[", i, "].rs : ", INST_INFO[i].rs)
            print("INST_INFO[", i, "].rt : ", INST_INFO[i].rt)
            print("INST_INFO[", i, "].imm : ",
                  INST_INFO[i].imm)

        # TYPE R
        # 0x0: (0x000000)ADD, ADDU, AND, NOR, OR, SLT, SLTU, SLL, SRL, SUB, SUBU  if JR
        elif INST_INFO[i].opcode == 0x0:
            print("INST_INFO[", i, "].func_code : ",
                  INST_INFO[i].func_code)
            print("INST_INFO[", i, "].rs : ",
                  INST_INFO[i].rs)
            print("INST_INFO[", i, "].rt : ",
                  INST_INFO[i].rt)
            print("INST_INFO[", i, "].rd : ",
                  INST_INFO[i].rd)
            print("INST_INFO[", i, "].shamt : ",
                  INST_INFO[i].shamt)

        # TYPE J
        # 0x2: (0x000010)J
        # 0x3: (0x000011)JAL
        elif INST_INFO[i].opcode == 0x2 or INST_INFO[i].opcode == 0x3:
            print("INST_INFO[", i, "].target : ",
                  INST_INFO[i].target)
        else:
            print("Not available instrution\n")

    print("Memory Dump - Text Segment\n")
    for i in range(0, initialize.text_size, 4):
        print("text_seg[", i, "] : ", "%x" %
              util.mem_read(util.MEM_TEXT_START + i))
    for i in range(0, initialize.data_size, 4):
        print("data_seg[", i, "] : ", "%x" %
              util.mem_read(util.MEM_DATA_START + i))
    print("Current PC: %x" % util.CURRENT_STATE.PC)
