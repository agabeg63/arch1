'''
MIPS-32 Instruction Level Simulatr

CSE261 UNIST
initialize.py
'''

import parse
import util

# Load machine language program
# and set up initial state of the machine
class MIPS:
    def __init__(self, path):
        self.path = path
        util.init_memory()
        self.load_program()
        util.RUN_BIT = True
        
    # Load program and service routines into mem
    def load_program(self):
        text_index = 0

        # Open program file
        file = open(self.path, 'r')
        if file == None:
            print("Error: Can't open program file ", self.path)
            exit(-1)

        # Read in the program
        ii = 0

        for line in file:
            line = line.rstrip('\n')

            # check text segment size
            global text_size
            text_size = util.fromBinary(line[:32])
            global NUM_INST
            NUM_INST = text_size//4

            # initial memory allocation of text segment
            global INST_INFO
            instruction = util.instruction()
            INST_INFO = [instruction] * (text_size//4)
            util.init_inst_info(NUM_INST)

            # check data semgent size
            global data_size
            data_size = util.fromBinary(line[32:64])

            buffer_count = len(line[64:])//32
            read_start = 64
            for i in range(buffer_count):
                buffer = line[read_start:read_start+32]  # read 32bits
                if ii < text_size:
                    INST_INFO[text_index] = parse.parse_instr(buffer, ii)
                    text_index += 1
                elif ii < text_size + data_size:
                    parse.parse_data(buffer, ii - text_size)
                ii += 4
                read_start += 32
            #########################
            # parse.print_parse_result(INST_INFO)
            ##########################

        util.CURRENT_STATE.PC = util.MEM_TEXT_START
        # print("Read ", ii/4, "words from program into memory.\n")
