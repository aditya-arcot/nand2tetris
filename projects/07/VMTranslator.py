import sys
import os

newline = '\n'

class Parser:
    def __init__(self, input_file_path):
        with open(input_file_path, 'r') as input_file:
            unfiltered_lines = input_file.readlines()

        self.lines = []
        for line in unfiltered_lines:
            line = line.strip()
            if line == "":
                continue
            args = line.split()
            if args[0] == '//':
                continue
            self.lines.append(line)

        self.ind = 0

    def hasMoreCommands(self):
        if self.ind <= len(self.lines) - 1:
            return True
        return False

    def advance(self):
        self.current_command = self.lines[self.ind]
        self.ind += 1


class CodeWriter:
    def __init__(self, output_file, filename):
        self.output_file = output_file
        self.filename = filename
        self.labelnum = 0

    def join_with_newline(self, lst):
        out = ''
        for i in lst:
            out += i + newline
        return out.strip()

    def write(self, command):
        self.output_file.write('// ' + command + newline)

        args = command.split()

        # implement other types in project 8
        if args[0] == 'push' or args[0] == 'pop':
            out = self.writePushPop(args)
        else:
            out = self.writeArithmeticLogical(args)

        self.output_file.write(out)
        self.output_file.write(newline + newline)

    def get_label_num(self):
        n = self.labelnum
        self.labelnum += 1
        return n

    def writeArithmeticLogical(self, args):
        cmd = args[0]
        n = self.get_label_num()

        if cmd == 'add':
            commands = ['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=D+M']
        elif cmd == 'sub':
            commands = ['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M-D']
        elif cmd == 'neg':
            commands = ['@SP', 'A=M-1', 'M=-M']
        elif cmd == 'eq' or cmd == 'gt' or cmd == 'lt':
            commands = self.comp(cmd, n)
        elif cmd == 'and':
            commands = ['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=D&M']
        elif cmd == 'or':
            commands = ['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=D|M']
        elif cmd == 'not':
            commands = ['@SP', 'A=M-1', 'M=!M']
        else:
            raise Exception('unrecognized operation')

        return self.join_with_newline(commands)

    def comp(self, cmd, n):
        return ['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'D=M-D', f'@TRUE{n}', \
                'D;J' + cmd.upper(), 'D=0', f'@FALSE{n}', '0;JMP', f'(TRUE{n})', \
                'D=-1', f'(FALSE{n})', '@SP', 'A=M-1', 'M=D']

    def writePushPop(self, args):
        cmd = args[0]
        segment = args[1]
        i = args[2]

        if cmd == 'push':
            if segment == 'constant':
                commands = self.push_constant(i)
            elif segment == 'temp':
                commands = self.push_temp(i)
            elif segment == 'local':
                commands = self.push_local(i)
            elif segment == 'argument':
                commands = self.push_argument(i)
            elif segment == 'this':
                commands = self.push_this(i)
            elif segment == 'that':
                commands = self.push_that(i)
            elif segment == 'pointer':
                commands = self.push_pointer(i)
            elif segment == 'static':
                commands = self.push_static(i)
            else:
                raise Exception('unrecognized segment')

            commands += self.push_core()

        else:
            if segment == 'temp':
                commands = self.pop_temp()
            elif segment == 'local':
                commands = self.pop_local()
            elif segment == 'argument':
                commands = self.pop_argument()
            elif segment == 'this':
                commands = self.pop_this()
            elif segment == 'that':
                commands = self.pop_that()
            elif segment == 'pointer':
                commands = self.pop_pointer()
            elif segment == 'static':
                commands = self.pop_static(i)
            else:
                raise Exception('unrecognized segment')

            if not segment == 'static':
                commands += self.pop_core(i)

        return self.join_with_newline(commands)

    def pop_core(self, i):
        return [f'@{i}', 'D=D+A', '@R13', 'M=D', '@SP', 'M=M-1', \
                'A=M', 'D=M', '@R13', 'A=M', 'M=D']

    def pop_temp(self):
        return ['@5', 'D=A']

    def pop_local(self):
        return ['@LCL', 'D=M']

    def pop_argument(self):
        return ['@ARG', 'D=M']

    def pop_this(self):
        return ['@THIS', 'D=M']

    def pop_that(self):
        return ['@THAT', 'D=M']

    def pop_pointer(self):
        return ['@THIS', 'D=A']

    def pop_static(self, i):
        return ['@SP', 'M=M-1', 'A=M', 'D=M', f'@{self.filename}.{i}', 'M=D']

    def push_core(self):
        return ['@SP', 'A=M', 'M=D', '@SP', 'M=M+1']

    def push_constant(self, i):
        return [f'@{i}', 'D=A']

    def push_temp(self, i):
        return ['@5', 'D=A', f'@{i}', 'A=D+A', 'D=M']

    def push_local(self, i):
        return ['@LCL', 'D=M', f'@{i}', 'A=D+A', 'D=M']

    def push_argument(self, i):
        return ['@ARG', 'D=M', f'@{i}', 'A=D+A', 'D=M']

    def push_this(self, i):
        return ['@THIS', 'D=M', f'@{i}', 'A=D+A', 'D=M']

    def push_that(self, i):
        return ['@THAT', 'D=M', f'@{i}', 'A=D+A', 'D=M']

    def push_static(self, i):
        return [f'@{self.filename}.{i}', 'D=M']

    def push_pointer(self, i):
        return ['@THIS', 'D=A', f'@{i}', 'A=D+A', 'D=M']


def main():
    if len(sys.argv) < 2:
        print('enter file name')
        return

    input_file_path = sys.argv[1]

    if not input_file_path.endswith('.vm'):
        print('supply .vm file')
        return

    if not os.path.isfile(input_file_path):
        print('file not found')
        return

    filename = os.path.split(input_file_path)[1].split('.')[0]
    output_file_path = '.'.join(input_file_path.split('.')[:-1]) + '.asm'

    with open(output_file_path, 'w') as output_file:
        parser = Parser(input_file_path)
        codeWriter = CodeWriter(output_file, filename)

        while parser.hasMoreCommands():
            parser.advance()
            codeWriter.write(parser.current_command)

main()
