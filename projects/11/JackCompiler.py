import os, sys

from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine

def parse_jack_file(path):
    '''parses input file'''

    tokenizer = JackTokenizer(path)
    #for i in tokenizer.tokens: print(i)

    output_path = '.'.join(path.split('.')[:-1]) + '.vm'
    compilation_engine = CompilationEngine()
    compilation_engine.compile(tokenizer, output_path)


def main():
    '''checks input, creates classes, generates XML for each file'''

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

        parse_jack_file(input_path)

    elif os.path.isdir(input_path):
        for i in os.listdir(input_path):
            if i.endswith('.jack'):
                parse_jack_file(os.path.join(input_path, i))

    else:
        print('enter either a file or folder')


main()
