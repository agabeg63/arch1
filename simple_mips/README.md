# CSE261 Project 2: MIPS Simulator
More details are in handout

# Instructions
There are three functions you need to implement, located in the following two files: `parse.py`, `run.py`

### 1. parse.py

**Implement** the following parsing functions.

```python
def parse_instr(buffer, index)
def parse_data(buffer, index)
```

The `parse_instr()` function is called for every instruction in the input file, and converts them into the `instruction` type.
The `instruction` type is defined in util.py

The `parse_data()` function is called for every data field in the input file, and you need to fill the data into the `simulated memory`.
Use the `mem_read` and `mem_write` as mentioned in the Hints section below.

There is a helper function you can use to convert binary strings to int variables:

```python
def fromBinary(bits)
```


### 2. run.py

**Implement** the following function:

```python
def process_instruction()
```

The `process_instruction()` function is used by the `cycle()` instruction to execute the instruction at the current PC.
Your internal register/memory state should be changed according to the instruction that is pointed to by the current PC.

## Hints

* Always use the `mem_read()`, `mem_write()` or `mem_write_half` functions when trying to read or write from the `simulated memory`.
This includes your implementation of the load/store functions, but also when you are loading `data` region to the `simulated memory`.
* You may generate input files of very simple instructions to check the functionality of your simulator. For example, `add $1, $1, 5`.
Then you can check if the R1 of your simulator has been incremented by 5, etc..
