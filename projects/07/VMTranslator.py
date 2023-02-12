'''translates VM code to Hack assembly symbolic code'''

import sys
import os

NEWLINE = '\n'

class Parser:
    '''reads, filters .vm file'''

    def __init__(self, input_file_path):
        with open(input_file_path, 'r', encoding='utf8') as input_file:
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
        self.current_command = None

    def has_more_commands(self):
        '''returns whether file has more commands'''

        if self.ind <= len(self.lines) - 1:
            return True
        return False

    def advance(self):
        '''advances current command and index'''

        self.current_command = self.lines[self.ind]
        self.ind += 1


class CodeWriter:
    '''converts VM code, writes to output file'''

    def __init__(self, output_file, filename):
        self.output_file = output_file
        self.filename = filename
        self.labelnum = 0

    def join_with_newline(self, lst):
        '''converts list into string separated by newlines'''

        out = ''
        for i in lst:
            out += i + NEWLINE
        return out.strip()

    def write(self, command):
        '''writes assembly code for a command'''

        self.output_file.write('// ' + command + NEWLINE)

        args = command.split()

        # implement other types in project 8
        if args[0] == 'push' or args[0] == 'pop':
            out = self.convert_memory_access(args)
        else:
            out = self.convert_arithmetic_logical(args)

        self.output_file.write(self.join_with_newline(out))
        self.output_file.write(NEWLINE + NEWLINE)

    def get_label_num(self):
        '''returns, advances label number'''

        temp = self.labelnum
        self.labelnum += 1
        return temp

    def convert_arithmetic_logical(self, args):
        '''returns arithmetic or logical assembly commands'''

        cmd = args[0]
        labelnum = self.get_label_num()

        if cmd == 'add':
            commands = ['M=D+M']
        elif cmd == 'sub':
            commands = ['M=M-D']
        elif cmd == 'and':
            commands = ['M=D&M']
        elif cmd == 'or':
            commands = ['M=D|M']
        elif cmd in ('eq', 'gt', 'lt'):
            commands = self.comp(cmd, labelnum)
        elif cmd == 'neg':
            return ['@SP', 'A=M-1', 'M=-M']
        elif cmd == 'not':
            return ['@SP', 'A=M-1', 'M=!M']
        else:
            raise Exception('unrecognized operation')

        return ['@SP', 'AM=M-1', 'D=M', 'A=A-1'] + commands

    def comp(self, cmd, num):
        '''returns assembly commands for VM comparisons'''

        return ['D=M-D', f'@TRUE{num}', 'D;J' + cmd.upper(), 'D=0', f'@FALSE{num}', \
                '0;JMP', f'(TRUE{num})', 'D=-1', f'(FALSE{num})', '@SP', 'A=M-1', 'M=D']

    def convert_memory_access(self, args):
        '''returns memory assembly commands'''

        cmd = args[0]
        segment = args[1]
        i = args[2]

        if segment == 'constant':
            commands = [f'@{i}', 'D=A']
        elif segment == 'temp':
            commands = ['@5', 'D=A']
        elif segment == 'local':
            commands = ['@LCL', 'D=M']
        elif segment == 'argument':
            commands = ['@ARG', 'D=M']
        elif segment == 'this':
            commands = ['@THIS', 'D=M']
        elif segment == 'that':
            commands = ['@THAT', 'D=M']
        elif segment == 'pointer':
            commands = ['@THIS', 'D=A']
        elif segment == 'static':
            if cmd == 'pop':
                return ['@SP', 'AM=M-1', 'D=M', f'@{self.filename}.{i}', 'M=D']
            commands = [f'@{self.filename}.{i}', 'D=M']
        else:
            raise Exception('unrecognized segment')

        if cmd == 'push':
            if not segment in ('constant', 'static'):
                commands += [f'@{i}', 'A=D+A', 'D=M']
            return commands + ['@SP', 'A=M', 'M=D', '@SP', 'M=M+1']

        return commands +[f'@{i}', 'D=D+A', '@R13', 'M=D', '@SP', 'AM=M-1', \
                        'D=M', '@R13', 'A=M', 'M=D']

def main():
    '''checks input, creates classes, iterates for each line'''

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

    with open(output_file_path, 'w', encoding='utf8') as output_file:
        parser = Parser(input_file_path)
        code_writer = CodeWriter(output_file, filename)

        while parser.has_more_commands():
            parser.advance()
            code_writer.write(parser.current_command)

main()
