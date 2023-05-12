'''
MIPS-32 Instruction Level Simulatr

CSE261 UNIST
util.py
'''
import initialize
import ctypes
import cache 

# Basic Information
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
MEM_GROW_UP=0
MEM_GROW_DOWN=-1

class mem_region_t:
    def __init__(self, start, size, type=MEM_GROW_UP):
        self.start = start
        self.size = size
        self.mem = []
        self.off_bound = -(size)*type #For useful memory dump
        self.type = type
        self.dirty = False

    def set_off_bound(self, off):
        self.dirty = True
            
        if self.type == MEM_GROW_UP:
            self.off_bound = max(off, self.off_bound)
        else:
            self.off_bound = min(off, self.off_bound)

    def init_bound(self):
        self.dirty = False

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


BLOCK_ADDR_MASK = ~(0b11111)
# Procedure: block_read
# Purpose: Read cacheline-size(32-Byte) data from Memory
def block_read(address):
    # mask address offset
    address = address & BLOCK_ADDR_MASK
    
    for SEGMENT in MEM_REGIONS:
        if address >= SEGMENT.start and address < (SEGMENT.start + SEGMENT.size):
            offset = address - SEGMENT.start
            return SEGMENT.mem[offset:offset+cache.CACHELINE_SIZE]
                    
# Procedure: block_write
# Purpose: Write cacheline-size data to Memory
def block_write(address, data):
    # mask address offset
    address = address & BLOCK_ADDR_MASK
    
    for SEGMENT in MEM_REGIONS:
        if address >= SEGMENT.start and address < (SEGMENT.start + SEGMENT.size):
            offset = address - SEGMENT.start
            SEGMENT.set_off_bound(offset+cache.CACHELINE_SIZE)
            SEGMENT.mem[offset:offset+cache.CACHELINE_SIZE] = data
            
# Procedure: mem_read
# Purpose: read a 32-bit word from memory
def mem_read(address):
    return cache.cache_read(address & 0xffffffff)


# Procedure: mem_write
# Purpose: Write a 32-bit word to memory
def mem_write(address, value):
    cache.cache_write(address & 0xffffffff, value)


# Procedure: cycle
# Purpose: Execute a cycle
def cycle():
    import run
    run.process_instruction()
    global INSTRUCTION_COUNT
    INSTRUCTION_COUNT += 1

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
    print(INSTRUCTION_COUNT, " - Current PC: %x" % CURRENT_STATE.PC)
    cache.cdump()
    
    if MEM_DATA.dirty:
        dstart, dstop = MEM_DATA.start, MEM_DATA.start+MEM_DATA.off_bound
        print("Data section [0x%8X..0x%8x] :" % (dstart, dstop))
        mdump(dstart,dstop-4)
        print("")
    
    if MEM_STACK.dirty:
        dstart, dstop = MEM_STACK.start+MEM_STACK.off_bound, MEM_STACK.start+MEM_STACK_SIZE
        print("Stack section [0x%8X..0x%8x] :" % (dstart, dstop))
        mdump(dstart,dstop-4)
        print("")
    
# Procedure: mdump
# Purpose: Dump a word-aligned region of memory to the output file.
def mdump(start, stop):
    # print("Memory content [0x%8X..0x%8x] :" % (start, stop))
    print("-------------------------------------")
    for b in range(start, stop+1, cache.CACHELINE_SIZE):
        line = f"{b:08x}...{(b+cache.CACHELINE_SIZE-BYTES_PER_WORD):08x}| " 
        block = block_read(b)
        
        for i in range(0, cache.CACHELINE_SIZE, BYTES_PER_WORD):
            word = (block[i+3] << 24) | (block[i+2] << 16) | (block[i+1] << 8) | (block[i] << 0)
            line+= f"{word:08x}."
            
        line +="|"
        print(line)
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