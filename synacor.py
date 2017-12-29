
import sys
import struct
from collections import deque
from os.path import join, dirname, getsize

MIN_REGISTER = 32768
MAX_VALID = 32775
HEX_15BIT = 0x7FFF
NUM_REGISTERS = 8

debug = False

class VirtualMachine:
    def __init__(self, arch_spec_path, binary_path):
        self.instructions_map = self.read_instructions_map(arch_spec_path)
        self.stack = deque()
        self.current_address = 0
        self.memory = self.read_memory(binary_path)
        self.registers = {}
        for register in range(MIN_REGISTER, MIN_REGISTER + NUM_REGISTERS):
            self.registers[register] = 0

    def read_instructions_map(self, input_path):
        with open(input_path) as f:
            lines = f.readlines()
        instructions_lines = lines[35::2]
        instructions = {}
        for i, line in enumerate(instructions_lines):
            name = line.split(':')[0]
            argc = len(line.split()) - 2
            instructions[i] = name, argc
        return instructions

    def read_memory(self, binary_path):
        memory = {}
        binary_num_words = getsize(binary_path) // 2
        with open(binary_path, 'rb') as f:
            for address in range(binary_num_words):
                memory[address] = self.read_word(f)
        return memory

    def read_next_instruction(self, file):
        address = file.tell() // 2
        instruction_code = self.read_word(file)
        while instruction_code not in self.instructions_map:
            if instruction_code is None:
                return None
            self.memory[address] = instruction_code
            instruction_code = self.read_word(file)
            address += 1
        name, argc = self.instructions_map[instruction_code]
        argv = self.read_words(file, n=argc)
        return address, name, argv

    def read_word(self, file):
        read_word = file.read(2)
        if not read_word:  # EOF
            return None
        number, = struct.unpack('<H', read_word)
        return number

    def read_words(self, file, n=1):
        return [self.read_word(file) for _ in range(n)]

    def parse(self, n):
        if n < 0 or n > MAX_VALID:
            raise ValueError('Invalid number:', n)
        elif n >= MIN_REGISTER:
            return self.registers[n]
        else:
            return n

    def fix_name(self, name):
        if name in ('and', 'or', 'not', 'in'):
            name += '_'
        return name

    def run_next_instruction(self):
        name, argv = self.memory[self.current_address]
        if name != 'out' and debug:
            print('\nRunning:', self.current_address, name, argv)
        argc = len(argv)
        self.current_address += 1 + argc
        getattr(self, self.fix_name(name))(*argv)
        if name != 'out' and debug:
            print('Registers after:', self.registers)

    def run(self):
        while True:
            self.run_next_instruction()


    ### INSTRUCTIONS ###
    def halt(self):
        sys.exit(0)

    def set(self, a, b):
        self.registers[a] = self.parse(b)

    def push(self, a):
        self.stack.append(self.parse(a))

    def pop(self, a):
        try:
            self.registers[a] = self.stack.pop()
        except IndexError:
            print('The stack is empty!')
            sys.exit(1)

    def eq(self, a, b, c):
        if self.parse(b) == self.parse(c):
            self.set(a, 1)
        else:
            self.set(a, 0)

    def gt(self, a, b, c):
        if self.parse(b) > self.parse(c):
            self.set(a, 1)
        else:
            self.set(a, 0)

    def jmp(self, a):
        self.current_address = self.parse(a)

    def jt(self, a, b):
        if self.parse(a) != 0:
            self.jmp(b)

    def jf(self, a, b):
        if self.parse(a) == 0:
            self.jmp(b)

    def add(self, a, b, c):
        result = (self.parse(b) + self.parse(c)) % MIN_REGISTER
        self.set(a, result)

    def mult(self, a, b, c):
        result = (self.parse(b) * self.parse(c)) % MIN_REGISTER
        self.set(a, result)

    def mod(self, a, b, c):
        result = self.parse(b) % self.parse(c)
        self.set(a, result)

    def and_(self, a, b, c):
        result = self.parse(b) & self.parse(c)
        self.set(a, result)

    def or_(self, a, b, c):
        result = self.parse(b) | self.parse(c)
        self.set(a, result)

    def not_(self, a, b):
        result = (~self.parse(b)) & HEX_15BIT
        self.set(a, result)

    def rmem(self, a, b):
        self.set(a, self.memory[self.parse(b)])

    def wmem(self, a, b):
        self.memory[self.parse(a)] = self.parse(b)

    def call(self, a):
        self.push(self.current_address)
        self.jmp(self.parse(a))

    def ret(self):
        try:
            self.jmp(self.stack.pop())
        except IndexError:
            self.halt()

    def out(self, a):
        print(chr(a), end='')

    def in_(self, a):
        self.set(ord(a), input())

    def noop(self):
        pass



def main():
    arch_spec_path = join(dirname(__file__), 'arch-spec')
    binary_path = join(dirname(__file__), 'challenge.bin')
    virtual_machine = VirtualMachine(arch_spec_path, binary_path)
    # virtual_machine.run()


if __name__ == '__main__':
    main()
