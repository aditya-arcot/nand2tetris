'''translates VM code to Hack assembly symbolic code'''

import sys
import os

NEWLINE = '\n'


def join_with_newline(lst):
    '''converts list into string separated by newlines'''

    out = ''
    for i in lst:
        out += i + NEWLINE
    return out #.strip()


class Parser:
    '''reads, filters .vm file'''

    def __init__(self, input_file_path):
        with open(input_file_path, 'r', encoding='utf8') as input_file:
            unfiltered_lines = input_file.readlines()

        self.lines = []
        for line in unfiltered_lines:
            line = line.strip()
            if line != "" and not line.startswith('//'):
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

    def write(self, command):
        '''writes assembly code for a command'''

        self.output_file.write('// ' + command + NEWLINE)

        args = command.split()

        if args[0] == 'push' or args[0] == 'pop':
            out = self.convert_memory_access(args)

        elif args[0] == 'label':
            out = [f'({args[1]})']

        elif args[0] == 'goto':
            out = [f'@{args[1]}', '0;JMP']

        elif args[0] == 'if-goto':
            out = ['@SP', 'AM=M-1', 'D=M', f'@{args[1]}', 'D;JNE']

        elif args[0] == 'function':
            name = args[1]
            n_local = int(args[2])
            out = [f'({name})']
            for _ in range(n_local):
                out += ['@0', 'D=A', '@SP', 'M=M+1','A=M-1', 'M=D'] # initialize local as 0

        elif args[0] == 'return':
            out = [
                # store LCL as end_frame
                '@LCL', 'D=M', '@end_frame', 'M=D',
                # get return address
                '@5', 'D=D-A', 'A=D', 'D=M', '@ret_addr', 'M=D',
                # reposition return value
                '@SP', 'M=M-1', 'A=M', 'D=M', '@ARG', 'A=M', 'M=D',
                # reposition SP
                '@ARG', 'D=M', '@SP', 'M=D+1',
                # restore THAT, store end_frame-n in R13
                '@end_frame', 'D=M', '@1', 'D=D-A', '@R13', 'M=D','A=D', 'D=M', '@THAT', 'M=D',
                # restore THIS
                '@R13', 'MD=M-1', 'A=D', 'D=M', '@THIS', 'M=D',
                # restore ARG
                '@R13', 'MD=M-1', 'A=D', 'D=M', '@ARG', 'M=D',
                # restore LCL
                '@R13', 'MD=M-1', 'A=D', 'D=M', '@LCL', 'M=D',
                # go to return address
                '@ret_addr', 'A=M', '0;JMP']

        elif args[0] == 'call':
            function = args[1]
            n_args = args[2]
            labelnum = self.get_label_num()

            out = [
                # push return address
                f'@{function}$ret.{labelnum}', 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1',
                # push LCL
                '@LCL', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1',
                # push ARG
                '@ARG', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1',
                # push THIS
                '@THIS', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1',
                # push THAT
                '@THAT', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1',
                # ARG = SP - 5 - n_args
                f'@{str(5 + int(n_args))}', 'D=A', '@SP', 'D=M-D', '@ARG', 'M=D',
                # LCL = SP
                '@SP', 'D=M', '@LCL', 'M=D',
                # goto function
                f'@{function}', '0;JMP',
                # declare return address label
                f'({function}$ret.{labelnum})']

        else:
            out = self.convert_arithmetic_logical(args)

        self.output_file.write(join_with_newline(out))
        self.output_file.write(NEWLINE + NEWLINE)

    def get_label_num(self):
        '''returns, advances label number'''

        temp = self.labelnum
        self.labelnum += 1
        return temp

    def convert_arithmetic_logical(self, args):
        '''returns arithmetic or logical assembly commands'''

        cmd = args[0]

        commands = ['@SP', 'AM=M-1', 'D=M', 'A=A-1']

        if cmd == 'add':
            commands += ['M=D+M']

        elif cmd == 'sub':
            commands += ['M=M-D']

        elif cmd == 'and':
            commands += ['M=D&M']

        elif cmd == 'or':
            commands += ['M=D|M']

        elif cmd in ('eq', 'gt', 'lt'):
            commands += self.comp(cmd)

        elif cmd == 'neg':
            return ['@SP', 'A=M-1', 'M=-M']

        elif cmd == 'not':
            return ['@SP', 'A=M-1', 'M=!M']

        else:
            print(f'unrecognized operation - {cmd}')
            sys.exit(0)

        return commands

    def comp(self, cmd):
        '''returns assembly commands for VM comparisons'''

        labelnum = self.get_label_num()
        return ['D=M-D', f'@TRUE{labelnum}', 'D;J' + cmd.upper(), 'D=0', f'@FALSE{labelnum}', \
                '0;JMP', f'(TRUE{labelnum})', 'D=-1', f'(FALSE{labelnum})', '@SP', 'A=M-1', 'M=D']

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
            print('unrecognized segment')
            sys.exit(0)

        if cmd == 'push':
            if not segment in ('constant', 'static'):
                commands += [f'@{i}', 'A=D+A', 'D=M']
            return commands + ['@SP', 'A=M', 'M=D', '@SP', 'M=M+1']

        return commands +[f'@{i}', 'D=D+A', '@R13', 'M=D', '@SP', 'AM=M-1', \
                        'D=M', '@R13', 'A=M', 'M=D']


def main():
    '''checks input, creates classes, iterates for each line'''

    if len(sys.argv) < 2:
        print('enter file / folder name')
        return

    input_path = sys.argv[1]

    if not os.path.exists(input_path):
        print('path does not exist')
        return

    if os.path.isfile(input_path):
        if not input_path.endswith('.vm'):
            print('supply .vm file')
            return

        filename = os.path.split(input_path)[1].split('.')[0]
        output_file_path = '.'.join(input_path.split('.')[:-1]) + '.asm'

        with open(output_file_path, 'w', encoding='utf8') as output_file:
            parser = Parser(input_path)
            code_writer = CodeWriter(output_file, filename)

            while parser.has_more_commands():
                parser.advance()
                code_writer.write(parser.current_command)

    elif os.path.isdir(input_path):
        dirname = os.path.basename(os.path.normpath(input_path))
        output_file_path = os.path.join(input_path, dirname + '.asm')

        with open(output_file_path, 'w', encoding='utf8') as output_file:
            bootstrap = ['// bootstrap', '@256', 'D=A', '@SP', 'M=D', NEWLINE]
            output_file.write(join_with_newline(bootstrap))

            CodeWriter(output_file, 'bootstrap').write('call Sys.init 0')

            for i in os.listdir(input_path):
                if i.endswith('.vm'):
                    filename = i.split('.')[0]
                    file_path = os.path.join(input_path, i)

                    parser = Parser(file_path)
                    code_writer = CodeWriter(output_file, filename)

                    while parser.has_more_commands():
                        parser.advance()
                        code_writer.write(parser.current_command)

    else:
        print('enter either a file or folder')

main()
