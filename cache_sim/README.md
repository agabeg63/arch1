# CSE261 Project 3: Cache Simulator

More details are in handout

## Instructions

* Your job is implementing 4-way set-associative cache including:
  * 32-byte cacheline size
  * 8 sets
  * Write back
  * LRU replacement

* You must done assignment2 for this project.
  * Before you start this project, fill `run.py` and `parse.py` files that you have implemented.

### Implement the following functions

```python
def cache_read(address):
def cache_write(address, value):
```

* The `cache_read` function is called for every load instruction. Specify cache hit/miss and do proper action.
* The `cache_write` function is called for every store instruction. Specify cache hit/miss and do proper action.
  * In this project, `sh`(opcode: 0x29) instruction will not be used.

## Hints

### Address translation layout

* 32-byte cacheline: log2(32) = 5 bit for offset
* 8-set: log2(8) = 3 bit for index
* tag: 32 - (5+3) = 24 bit

```
 31                                     8 7           5 4                    0
  +--------------------------------------+-------------+---------------------+
  |              tag(24bit)              | index(3bit) |     offset(5bit)    |
  +--------------------------------------+-------------+---------------------+
```

### Data transfer call flow

```
                                                      [word-size transfer]                      [block-size transfer]
                                                            (4byte)                                   (32byte)    
 +-------------+                      +-----------+                            +-----------+                            +----------+
 |             |  load/store instr    | processor |       cache_read()         |           |        block_read()        |          |
 |   program   | ------------------>  |           |  <----------------------   |   cache   |  <----------------------   |  memory  |
 |             |                      | (register)|  ---------------------->   |           |  ---------------------->   |          |
 +-------------+                      +-----------+       cache_write()        +-----------+        blcok_write()       +----------+

    
```

### An empty cache layout

```
|index| v |  tag   |               way0              | v |  tag   |               way1              | v |  tag   |               way2              | v |  tag   |               way3              |
+-----+---+------------------------------------------+---+--------+---------------------------------+---+--------+---------------------------------+---+--------+---------------------------------+
| 000 | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... |
| 001 | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... |
| 010 | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... |
| 011 | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... |
| 100 | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... |
| 101 | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... |
| 110 | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... |
| 111 | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... | 0 | 000000 | ...cache block data (32byte)... |


```
