
import sys
import struct
from os.path import join, dirname
from collections import deque, defaultdict

def read_instructions_map(input_path):
    with open(input_path) as f:
        lines = f.readlines()
    instructions_lines = lines[35::2]
    instructions = {}
    for i, line in enumerate(instructions_lines):
        name = line.split(':')[0]
        argc = len(line.split()) - 2
        instructions[i] = name, argc
    return instructions


class VirtualMachine:
    def __init__(self, arch_spec_path, binary_path):
        self.instructions_map = read_instructions_map(arch_spec_path)
        self.stack = deque()
        self.registers = defaultdict(int)
        self.binary_file = None
        self.current_address = 0
        self.memory = self.read_program(binary_path)

    def read_program(self, binary_path):
        memory = {}
        with open(binary_path, 'rb') as f:
            # while True:
            for _ in range(350):
                next_instruction = self.read_next_instruction(f)
                if next_instruction is None:
                    return memory
                if next_instruction is not None:
                    # print(next_instruction)
                    address, name, argv = next_instruction
                    memory[address] = name, argv
        return memory

    def read_next_instruction(self, file):
        address = file.tell() // 2
        instruction_code = self.read_word(file)
        # print(address, instruction_code)
        if instruction_code == '':  # EOF
            return None
        name, argc = self.instructions_map[instruction_code]
        argv = self.read_words(file, n=argc)
        return address, name, argv

    def read_word(self, file):
        read_word = file.read(2)
        # print(read_word)
        word, = struct.unpack('<H', read_word)
        return word

    def read_words(self, file, n=1):
        return [self.read_word(file) for _ in range(n)]

    def translate(self, n):
        if n <  32768:
            return n
        elif n >= 32768:
            return self.registers[n - 32768]
        else:
            raise ValueError('Invalid number:', n)

    def halt(self):
        sys.exit(0)

    def set(self, a, b):
        self.registers[a] = self.registers[b]

    def push(self, a):
        self.stack.append(a)

    def pop(self, a):
        try:
            self.registers[a] = self.stack.pop()
        except IndexError:
            print('The stack is empty!')
            sys.exit(1)

    def eq(self, a, b, c):
        self.registers[a] = 1 if self.registers[b] == self.registers[c] else 0

    def gt(self, a, b, c):
        self.registers[a] = 1 if self.registers[b] > self.registers[c] else 0

    def jmp(self, a):
        self.current_address = self.regis

    def out(self, a):
        print(chr(a), end='')

    def noop(self):
        pass

    def run_next_instruction(self):
        name, argv = self.memory[self.current_address]
        argc = len(argv)
        self.current_address += 1 + argc
        # print('Running', name, argv)
        getattr(self, name)(*argv)


        # argc = len(argv)
        #
        # if argc > 0:
        #     a = argv[0]
        # if argc > 1:
        #     b = argv[1]
        # if argc > 2:
        #     c = argv[2]
        #
        # if name == 'halt':
        #     return False
        # elif name == 'set':
        #     self.registers[a] = b
        # elif name == 'push':
        #     self.stack.append(a)
        # elif name == 'pop':
        #     try:
        #         self.registers[a] = self.stack.pop()
        #     except IndexError:
        #         print('The stack is empty!')
        #         return False
        # elif name == 'eq':
        #     a = 1 if b == c else 0
        # elif name == 'gt':
        #     a = 1 if b == c else 0
        # elif name == 'jmp':
        #     self.current_address = a
        # else:
        #     pass # TODO
        # return True

    def run(self):
        while True:
            self.run_next_instruction()


def main():
    arch_spec_path = join(dirname(__file__), 'arch-spec')
    binary_path = join(dirname(__file__), 'challenge.bin')
    virtual_machine = VirtualMachine(arch_spec_path, binary_path)
    virtual_machine.run()


if __name__ == '__main__':
    main()
