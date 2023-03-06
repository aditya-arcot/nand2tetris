import os
import sys

from Tokenizer import Tokenizer
from CompilationEngine import CompilationEngine

def compile_jack_file(path):
    '''generates VM file from Jack file'''

    output_path = '.'.join(path.split('.')[:-1]) + '.vm'
    compilation_engine = CompilationEngine(Tokenizer(path))
    compilation_engine.compile(output_path)


def main():
    '''checks input, creates classes, generates VM output file for each Jack file'''

    if len(sys.argv) < 2:
        print('enter file / folder name')
        return

    input_path = sys.argv[1]

    if not os.path.exists(input_path):
        print('path does not exist')
        return

    if os.path.isfile(input_path):
        if not input_path.endswith('.jack'):
            print('supply .jack file')
            return

        if not os.path.isfile(input_path):
            print('file not found')
            return

        compile_jack_file(input_path)

    elif os.path.isdir(input_path):
        for i in os.listdir(input_path):
            if i.endswith('.jack'):
                compile_jack_file(os.path.join(input_path, i))

    else:
        print('enter either a file or folder')


main()
