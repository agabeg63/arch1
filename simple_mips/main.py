'''
MIPS-32 Instruction Level Simulatr

CSE261 UNIST
main.py
'''

import initialize
import util
import sys

count = 1
addr1 = 0
addr2 = 0
num_inst = 0
i = 100  # for loop

debug_set = 0
num_inst_set = 0
debug_interval = 1

argc = len(sys.argv)

# Error Checking
if argc < 2:
    print("Error: usage: ",
          sys.argv[0], " [-d debug_interval] [-n num_instr] inputBinary")
    exit(1)

mips = initialize.MIPS(sys.argv[argc-1])

# for checking parse result
# parse.print_parse_result(initialize.INST_INFO)

while count != argc - 1:
    if (sys.argv[count] == '-d'):
        debug_set = 1
        count += 1
        debug_interval = int(sys.argv[count], 10)
    elif (sys.argv[count] == '-n'):
        count += 1
        num_inst = int(sys.argv[count], 10)
        num_inst_set = 1
    else:
        print("Error: usage: ",
              sys.argv[0], " [-d debug_interval] [-n num_instr] inputBinary")
        exit(1)
    count += 1

if num_inst_set:
    i = num_inst

if debug_set:
    print("Simulating for %d cycles...\n" % i)

    while i > 0:
        util.cycle()
        
        if util.RUN_BIT == False:
            print("Simulator halted\n")
            # util.rdump()
            util.dump_memory()
            break
        
        if (num_inst-i) % debug_interval == 0:
            # util.rdump()
            util.dump_memory()
    
        i -= 1

else:
    util.running(i)
    # util.rdump()
    util.dump_memory()
