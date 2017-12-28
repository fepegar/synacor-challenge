
from os.path import join, dirname

def read_instructions(input_path):
    with open(input_path) as f:
        lines = f.readlines()
    instructions_lines = lines[35::2]
    instructions = {}
    for i, line in enumerate(instructions_lines):
        name = line.split(':')[0]
        nargs = len(line.split()) - 2
        instructions[i] = name, nargs
    return instructions
