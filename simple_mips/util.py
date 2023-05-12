'''
MIPS-32 Instruction Level Simulatr

CSE261 UNIST
util.py
'''
import initialize
import ctypes

# Basic Information
MEM_TEXT_START = 0x00400000
MEM_TEXT_SIZE = 0x00100000

#DATA section
MEM_DATA_START = 0x10000000
MEM_DATA_SIZE = 0x00100000

#STACK section
MEM_STACK_START = 0x80000000
MEM_STACK_SIZE = 0x00100000

MIPS_REGS = 32
BYTES_PER_WORD = 4


class CPU_State:
    def __init__(self):
        self.PC = 0  # program counter
        self.REGS = [0] * MIPS_REGS    # register file
        self.REGS[29] = MEM_STACK_START # initialize $sp

# You should decode your instructions from the
# ASCII-binary format to this structured format
class instruction:
    def __init__(self):
        # short
        self.opcode = 0
        # short
        self.func_code = 0
        # uint32_t
        self.value = 0
        # uint32_t
        self.target = 0
        # unsinged char
        self.rs = 0
        # unsinged char
        self.rt = 0
        # short
        self.imm = 0
        # unsinged char
        self.rd = 0
        # unsinged char
        self.shamt = 0


#  All simulated memory will be managed by this class
#  use the mem_write and mem_read functions to
#  access/modify the simulated memory
MEM_GROW_UP=1
MEM_GROW_DOWN=-1

class mem_region_t:
    def __init__(self, start, size, type=MEM_GROW_UP):
        self.start = start
        self.size = size
        self.mem = []
        self.off_bound = -(size-4)*type #For useful memory dump
        self.type = type
        self.dirty = False

    def set_off_bound(self, off):
        self.dirty = True
            
        if self.type == MEM_GROW_UP:
            self.off_bound = max(off, self.off_bound)
        else:
            self.off_bound = min(off, self.off_bound)

# Main memory
# memory will be dynamically allocated at initialization
MEM_TEXT = mem_region_t(MEM_TEXT_START, MEM_TEXT_SIZE)
MEM_DATA = mem_region_t(MEM_DATA_START, MEM_DATA_SIZE)
MEM_STACK = mem_region_t(MEM_STACK_START-MEM_STACK_SIZE, MEM_STACK_SIZE, MEM_GROW_DOWN)
MEM_REGIONS = [MEM_TEXT, MEM_DATA, MEM_STACK]
MEM_NREGIONS = 3

# CPU State info
CURRENT_STATE = CPU_State()
RUN_BIT = 0
INSTRUCTION_COUNT = 0


# Procedure: fromBinary
# Purpose: From binary to integer
def fromBinary(bits):
    eq = 0
    m = 1
    for bit in bits[::-1]:
        b = int(bit)
        eq += b * m
        m *= 2
    return eq


# Procedure: mem_read
# Purpose: read a 32-bit word from memory
def mem_read(address):
    for i in range(MEM_NREGIONS):
        if address >= MEM_REGIONS[i].start and address < (MEM_REGIONS[i].start + MEM_REGIONS[i].size):
            offset = address - MEM_REGIONS[i].start
            return (MEM_REGIONS[i].mem[offset + 3] << 24) | (MEM_REGIONS[i].mem[offset + 2] << 16) | (MEM_REGIONS[i].mem[offset + 1] << 8) | (MEM_REGIONS[i].mem[offset + 0] << 0)


# Procedure: mem_write
# Purpose: Write a 32-bit word to memory
def mem_write(address, value):
    for i in range(MEM_NREGIONS):
        if address >= MEM_REGIONS[i].start and address < (MEM_REGIONS[i].start + MEM_REGIONS[i].size):
            offset = address - MEM_REGIONS[i].start

            MEM_REGIONS[i].mem[offset + 3] = (value >> 24) & 0xFF
            MEM_REGIONS[i].mem[offset + 2] = (value >> 16) & 0xFF
            MEM_REGIONS[i].mem[offset + 1] = (value >> 8) & 0xFF
            MEM_REGIONS[i].mem[offset + 0] = (value >> 0) & 0xFF

            MEM_REGIONS[i].set_off_bound(offset+4)
            
# Procedure: mem_write_half
# Purpose: Write a half of 32-bit word to memory
def mem_write_half(address, value):
    for i in range(MEM_NREGIONS):
        if address >= MEM_REGIONS[i].start and address < (MEM_REGIONS[i].start + MEM_REGIONS[i].size):
            offset = address - MEM_REGIONS[i].start

            MEM_REGIONS[i].mem[offset + 1] = (value >> 8) & 0xFF
            MEM_REGIONS[i].mem[offset + 0] = (value >> 0) & 0xFF
            
            MEM_REGIONS[i].set_off_bound(offset+2)

# Procedure: cycle
# Purpose: Execute a cycle
def cycle():
    import run
    run.process_instruction()
    global INSTRUCTION_COUNT
    INSTRUCTION_COUNT += 1

    # for debug
    # print(INSTRUCTION_COUNT, " - Current PC: %x" % CURRENT_STATE.PC)


# Procedure: run n
# Purpose: Simulate MIPS for n cycles
def running(num_cycles):
    if RUN_BIT == False:
        print("Can't simulate, Simulator is halted\n")
        return
    print("Simulating for %d cycles...\n" % num_cycles)
    for i in range(num_cycles):
        if RUN_BIT == False:
            print("Simulator halted\n")
            break
        cycle()


# Procedure: go
# Purpose: Simulate MIPS until HALTed
def go():
    if RUN_BIT == False:
        print("Can't simulate, Simulator is halted\n")
        return
    print("Simulating...\n")
    while RUN_BIT:
        cycle()
    print("Simulator halted\n")



def dump_memory():
    if MEM_DATA.dirty:
        dstart, dstop = MEM_DATA.start, MEM_DATA.start+MEM_DATA.off_bound
        print("Data section [0x%8X..0x%8x] :" % (dstart, dstop))
        mdump(dstart,dstop)
        print("")
    
    if MEM_STACK.dirty:
        dstart, dstop = MEM_STACK.start+MEM_STACK.off_bound, MEM_STACK.start+MEM_STACK_SIZE-4
        print("Stack section [0x%8X..0x%8x] :" % (dstart, dstop))
        mdump(dstart,dstop)
        print("")
    
# Procedure: mdump
# Purpose: Dump a word-aligned region of memory to the output file.
def mdump(start, stop):
    # print("Memory content [0x%8X..0x%8x] :" % (start, stop))
    print("-------------------------------------")
    for i in range(start, stop+1, 4):
        print("0x%08x: 0x%08x" % (i, mem_read(i)))
    print("")


# Procedure: rdump
# Purpose:  Dump current register and bus values to the output file.
def rdump():
    print("Current register values :")
    print("-------------------------------------")
    print("PC: 0x%08x" % CURRENT_STATE.PC)
    print("Registers:")
    for k in range(MIPS_REGS):
        print("R%d: 0x%08x" % (k, ctypes.c_uint(CURRENT_STATE.REGS[k]).value))
    print("")


# Procedure : init_memory
# Purpose : Allocate and zero memory
def init_memory():
    for i in range(MEM_NREGIONS):
        MEM_REGIONS[i].mem = [0] * MEM_REGIONS[i].size


# Procedure : init_inst_info
# Purpose : Initialize instruction info
def init_inst_info(NUM_INST):
    for i in range(NUM_INST):
        initialize.INST_INFO[i].value = 0
        initialize.INST_INFO[i].opcode = 0
        initialize.INST_INFO[i].func_code = 0
        initialize.INST_INFO[i].rs = 0
        initialize.INST_INFO[i].rt = 0
        initialize.INST_INFO[i].rd = 0
        initialize.INST_INFO[i].imm = 0
        initialize.INST_INFO[i].shamt = 0
        initialize.INST_INFO[i].target = 0
