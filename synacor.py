
import sys
import struct
from collections import deque
from os.path import join, dirname, getsize

MIN_REGISTER = 32768
MAX_VALID = 32775
HEX_15BIT = 0x7FFF
NUM_REGISTERS = 8


class VirtualMachine:
    def __init__(self, arch_spec_path, binary_path, disassemble_path):
        self.instructions_map = self.read_instructions_map(arch_spec_path)
        self.stack = deque()
        self.current_address = 0
        self.memory = self.read_memory(binary_path)
        self.disassemble_path = disassemble_path
        self.registers = {}
        for register in range(MIN_REGISTER, MIN_REGISTER + NUM_REGISTERS):
            self.registers[register] = 0
        if len(sys.argv) == 2 and sys.argv[1] == '-a':
            import answers
            self.input_stack = answers.get_answers()
            self.input_writing = deque(self.input_stack.popleft())
        else:
            self.input_stack = []
            self.input_writing = ''
        self.debug = False

    @staticmethod
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

    def read_memory(self, binary_path):
        memory = {}
        binary_num_words = getsize(binary_path) // 2
        with open(binary_path, 'rb') as f:
            for address in range(binary_num_words):
                memory[address] = self.read_word(f)
        return memory

    def disassemble(self):
        print('(Disassembling)')
        save_address = self.current_address
        self.current_address = 0
        with open(self.disassemble_path, 'w') as f:
            memory_blocks = 0
            writing = ''
            while self.current_address < len(self.memory):
                instruction_code = self.read_from_memory()[0]
                if instruction_code not in self.instructions_map:
                    memory_blocks += 1
                    memory_block_address = self.current_address
                    continue
                else:
                    if memory_blocks:
                        print(f'{memory_block_address:5}   memory x{memory_blocks}', file=f)
                        memory_blocks = 0

                name, argc = self.instructions_map[instruction_code]
                argv = self.read_from_memory(n=argc)

                if name == 'out':
                    writing += chr(argv[0])
                    continue

                if writing:
                    address = self.current_address - 2 * len(writing) + 1
                    string = f'{address:5}   out   {writing.strip()}'
                    # print(writing)
                    print(string, file=f)
                    writing = ''

                argv = [self.parse(n, string=True) for n in argv]

                argv = list(map(lambda x: f'{str(x):5}', argv))
                argv = ' '.join(argv) if argv else ''
                string = f'{self.current_address:5}   {name:5} {argv}'

                # Identify functions
                if name == 'ret':
                    string += '\n'

                print(string, file=f)
        self.current_address = save_address

    @staticmethod
    def read_word(file):
        read_word = file.read(2)
        if not read_word:  # EOF
            return None
        number, = struct.unpack('<H', read_word)
        return number

    def parse(self, n, string=False):
        if n < 0 or n > MAX_VALID:
            raise ValueError('Invalid number:', n)
        elif n >= MIN_REGISTER:
            if string:
                return f'reg{n - MIN_REGISTER}'
            else:
                return self.registers[n]
        else:
            return n

    @staticmethod
    def fix_name(name):
        if name in ('and', 'or', 'not', 'in'):
            name += '_'
        return name

    def read_from_memory(self, n=1):
        read = []
        for _ in range(n):
            read.append(self.memory[self.current_address])
            self.current_address += 1
        return read

    def run_next_instruction(self):
        instruction_code = self.read_from_memory()[0]
        name, argc = self.instructions_map[instruction_code]
        argv = self.read_from_memory(n=argc)
        if name != 'out' and self.debug:
            print('Running:', self.current_address, name, argv)
        getattr(self, self.fix_name(name))(*argv)

    def print_registers(self):
        print('Registers:')
        for k, v in self.registers.items():
            print(f'{self.parse(k, string=True)}: {v}')

    def print_stack(self):
        print('Stack:')
        for address in self.stack:
            print(address)
        print()

    def run(self):
        while True:
            self.run_next_instruction()


    ### INSTRUCTIONS ###
    @staticmethod
    def halt():
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
        char = chr(self.parse(a))
        print(char, end='')

    def in_(self, a):
        if self.input_writing:
            c = self.input_writing.popleft()
            print(c, end='')
        elif self.input_stack:
            self.input_writing = deque(self.input_stack.popleft())
            c = self.input_writing.popleft()
            print(c, end='')
        else:
            c = sys.stdin.read(1)
            if c == '¿':
                command = input('Command (dump/debug/nodebug/hack): ')
                if command == 'dump':
                    print('Im here')
                    self.print_registers()
                    self.print_stack()
                elif command == 'debug':
                    self.debug = True
                elif command == 'nodebug':
                    self.debug = False
                elif command == 'hack':
                    self.hack_teleporter()
        num = ord(c)
        self.set(a, num)

    @staticmethod
    def noop():
        pass

    def hack_teleporter(self):
        print('Fixing teleporter...')

        n = 25734
        self.registers[MAX_VALID] = n

        # set $0, 6
        self.memory[6027] = 1
        self.memory[6028] = 32768
        self.memory[6029] = 6

        # ret
        self.memory[6030] = 18


def main():
    arch_spec_path = join(dirname(__file__), 'arch-spec')
    binary_path = join(dirname(__file__), 'challenge.bin')
    disassemble_path = join(dirname(__file__), 'disassemble.txt')
    virtual_machine = VirtualMachine(arch_spec_path, binary_path, disassemble_path)
    virtual_machine.run()


if __name__ == '__main__':
    main()
