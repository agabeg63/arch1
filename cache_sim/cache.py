'''
MIPS-32 Instruction Level Simulatr

CSE261 UNIST
cache.py
'''
from audioop import add
import re

from numpy import block
import util

######################
# Do not Modify Here
#
CACHELINE_SIZE = 32
ASSOCIATIVITY = 4
N_SETS = 8

class BLOCK:
    def __init__(self):
        self.valid=0
        self.tag=0
        self.data=[0x00]*CACHELINE_SIZE

class SET:
    def __init__(self):
        self.blocks = [BLOCK() for i in range(ASSOCIATIVITY)]
        self.history = [3,2,1,0] # Access history for LRU replacement
        
CACHE = [SET() for i in range(N_SETS)]

def init():
    return [SET() for i in range(N_SETS)]


def cdump():    
    print("Cache content:")
    
    empty = " "*34
    print(f"|index| v |  tag   | {empty}way0{empty} | v |  tag   | {empty}way1{empty} | v |  tag   | {empty}way2{empty} | v |  tag   | {empty}way3{empty} |")
    
    idx = 0
    for set in CACHE:
        pline = f"| {idx:03b} |"
        for b in set.blocks:
            data = 0
            data_str = ""
            cnt = 0
            for byte in b.data:
                data |= byte << cnt*8
                cnt +=1
                if cnt == 4:
                    data_str += f"{data:08x}."
                    data = 0
                    cnt = 0                
            pline += f" {b.valid} | {b.tag:06x} | {data_str} |"        
        print(pline)
        idx += 1
    
    print("")
    
#  You can modify below this line
#################################################

def turnBinary(address):
    return(format(address, '032b'))

# Procedure: cache_read
# Purpose: read a 32-bit word from cache
def cache_read(address):
    tag, idx, offset = 0,0,0
    #hit
    bina = turnBinary(address)
    tag = util.fromBinary(bina[0:24])
    idx = util.fromBinary(bina[24:27])
    offset = util.fromBinary(bina[27:])

    i = 0
    small_lru = 0
    for blk in CACHE[idx].blocks:
        #hit
        if blk.tag == tag and blk.valid == 1:
            CACHE[idx].history.remove(i)
            CACHE[idx].history.insert(0,i)
            return (blk.data[offset + 3] << 24) | (blk.data[offset + 2] << 16) | (blk.data[offset + 1] << 8) | (blk.data[offset + 0] << 0)
        
        i+=1
    #miss
    if CACHE[idx].blocks[CACHE[idx].history[3]].valid == 1 and CACHE[idx].blocks[CACHE[idx].history[3]].tag != tag:
        small_lru = CACHE[idx].history[3]
        util.block_write(((CACHE[idx].blocks[small_lru].tag << 3 + idx )<< 5), CACHE[idx].blocks[small_lru].data)
        CACHE[idx].blocks[small_lru].tag = tag
        CACHE[idx].blocks[small_lru].data = util.block_read(address)
        CACHE[idx].history.remove(small_lru)
        CACHE[idx].history.insert(0,small_lru)
        return (CACHE[idx].blocks[small_lru].data[offset + 3] << 24) | (CACHE[idx].blocks[small_lru].data[offset + 2] << 16) | (CACHE[idx].blocks[small_lru].data[offset + 1] << 8) | (CACHE[idx].blocks[small_lru].data[offset + 0] << 0)   
    else: 
        small_lru = CACHE[idx].history[3]
        CACHE[idx].blocks[small_lru].data = util.block_read(address)
        CACHE[idx].blocks[small_lru].valid = 1
        CACHE[idx].blocks[small_lru].tag = tag
        CACHE[idx].history.remove(small_lru)
        CACHE[idx].history.insert(0,small_lru)
        return (CACHE[idx].blocks[small_lru].data[offset + 3] << 24) | (CACHE[idx].blocks[small_lru].data[offset + 2] << 16) | (CACHE[idx].blocks[small_lru].data[offset + 1] << 8) | (CACHE[idx].blocks[small_lru].data[offset + 0] << 0)   
        

# Procedure: cache_write
# Purpose: Write a 32-bit word
def cache_write(address, value):
    tag, idx, offset = 0,0,0
    #hit
    bina = format(address, '032b')
    tag = util.fromBinary(bina[0:24])
    idx = util.fromBinary(bina[24:27])
    offset = util.fromBinary(bina[27:])
    print("offset: ", offset)

    i = 0
    small_lru = 0
    for blk in CACHE[idx].blocks:
        #hit
        if blk.tag == tag and blk.valid == 1:
            CACHE[idx].history.remove(i)
            CACHE[idx].history.insert(0,i)
            blk.data[offset + 3] = (value >> 24) & 0xFF
            blk.data[offset + 2] = (value >> 16) & 0xFF
            blk.data[offset + 1] = (value >> 8) & 0xFF
            blk.data[offset + 0] = (value >> 0) & 0xFF
            return
        i+=1
    #miss
    if CACHE[idx].blocks[CACHE[idx].history[3]].valid == 1:
        if CACHE[idx].blocks[CACHE[idx].history[3]].tag != tag:
            small_lru = CACHE[idx].history[3]
            util.block_write(((CACHE[idx].blocks[small_lru].tag << 3 + idx )<< 5), CACHE[idx].blocks[small_lru].data)
            CACHE[idx].blocks[small_lru].tag = tag
            CACHE[idx].blocks[small_lru].data = util.block_read(address)
            CACHE[idx].history.remove(small_lru)
            CACHE[idx].history.insert(0,small_lru)
        else:
            pass
    else: 
        small_lru = CACHE[idx].history[3]
        CACHE[idx].blocks[small_lru].data = util.block_read(address)
        CACHE[idx].blocks[small_lru].valid = 1
        CACHE[idx].blocks[small_lru].tag = tag
        CACHE[idx].history.remove(small_lru)
        CACHE[idx].history.insert(0,small_lru)

    #putting the data
    print(small_lru)
    CACHE[idx].blocks[small_lru].data[offset + 3] = (value >> 24) & 0xFF
    CACHE[idx].blocks[small_lru].data[offset + 2] = (value >> 16) & 0xFF
    CACHE[idx].blocks[small_lru].data[offset + 1] = (value >> 8) & 0xFF
    CACHE[idx].blocks[small_lru].data[offset + 0] = (value >> 0) & 0xFF
