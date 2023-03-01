'''part 1 of compiler - tokenizer and parser generate XML to be used by code generator'''

import os
import sys

NEWLINE = '\n'

KEYWORD = 0
SYMBOL = 1
INTEGER_CONSTANT = 2
STRING_CONSTANT = 3
IDENTIFIER = 4

keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', \
            'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', \
            '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']


class JackTokenizer:
    '''
    generates tokens from input file
    allows sequential access to tokens
    '''

    def __init__(self, input_path, output_path):
        self.tokens = []
        self.current_pos = -1

        self.create_tokens(input_path, output_path)


    def has_more_tokens(self):
        '''checks if more tokens exist'''
        if self.current_pos == len(self.tokens) - 1:
            return False
        return True


    def advance(self):
        '''advances to next token, returns it'''
        self.current_pos += 1
        return self.tokens[self.current_pos]


    def create_tokens(self, input_path, output_path):
        '''
        splits input file into tokens
        outputs result to tokens list and XML
        '''

        with open(input_path, 'r', encoding='utf8') as infile:
            lines = infile.readlines()

        filtered_lines = []
        # remove // onwards
        for line in lines:
            filtered_lines.append(line.split('//')[0])
        # remove block comments
        filtered_lines = self.remove_block_comments(filtered_lines)
        # remove empty lines
        filtered_lines = [i.strip() for i in filtered_lines if i.strip() != '']

        with open(output_path, 'w', encoding='utf8') as outfile:
            outfile.write('<tokens>' + NEWLINE)

            for i in filtered_lines:
                self.tokenize(i, outfile)

            outfile.write('</tokens>' + NEWLINE)


    def remove_block_comments(self, lines):
        '''
        removes block comments starting with /* and ending with */
        returns remaining lines
        '''

        block_comment = False
        block_comment_end_symbol = -1

        filtered = []

        for line in lines:
            out = ''

            for i, char in enumerate(line):
                if block_comment:
                    if char == '*':
                        block_comment_end_symbol = 0
                    elif char == '/':
                        if block_comment_end_symbol == 0:
                            block_comment_end_symbol = -1
                            block_comment = False
                    else:
                        block_comment_end_symbol = -1
                else:
                    if (char == '/') & (i != len(line) - 1):
                        if line[i+1] == '*':
                            block_comment = True
                        else:
                            out += char
                    else:
                        out += char

            filtered.append(out.strip())

        return filtered


    def tokenize(self, line, outfile):
        '''
        generates tokens from line of input file
        '''

        quote = False
        text = ''

        for i in line:
            if quote:
                if i == "\"":
                    self.write_string_constant(text, outfile)
                    quote = False
                    text = ''
                else:
                    text += i

            elif i == "\"":
                quote = True

            elif i in symbols:
                if len(text) > 0:
                    self.write_uncertain(text, outfile)
                    text = ''
                self.write_symbol(i, outfile)

            elif i == ' ':
                if len(text) > 0:
                    self.write_uncertain(text, outfile)
                    text = ''

            else:
                text += i

        if len(text) > 0:
            self.write_uncertain(text, outfile)


    def write_uncertain(self, text, outfile):
        '''
        determines token type
        writes to XML, stores in tokens list
        '''

        if text in keywords:
            self.write_keyword(text, outfile)
        elif text.isnumeric():
            self.write_integer_constant(text, outfile)
        else:
            self.write_identifier(text, outfile)


    def write_integer_constant(self, text, outfile):
        '''writes integer constant to XML, stores in tokens list'''
        outfile.write('<integerConstant> ')
        outfile.write(text)
        outfile.write(' </integerConstant>' + NEWLINE)
        self.tokens.append([INTEGER_CONSTANT, text])


    def write_string_constant(self, text, outfile):
        '''writes string constant to XML, stores in tokens list'''
        outfile.write('<stringConstant> ')
        outfile.write(text)
        outfile.write(' </stringConstant>' + NEWLINE)
        self.tokens.append([STRING_CONSTANT, text])


    def write_keyword(self, text, outfile):
        '''writes keyword to XML, stores in tokens list'''
        outfile.write('<keyword> ')
        outfile.write(text)
        outfile.write(' </keyword>' + NEWLINE)
        self.tokens.append([KEYWORD, text])


    def write_identifier(self, text, outfile):
        '''writes identifier to XML, stores in tokens list'''
        outfile.write('<identifier> ')
        outfile.write(text)
        outfile.write(' </identifier>' + NEWLINE)
        self.tokens.append([IDENTIFIER, text])


    def write_symbol(self, text, outfile):
        '''writes symbol to XML, stores in tokens list'''
        self.tokens.append([SYMBOL, text])

        if text == '>':
            text = '&gt;'
        elif text == '<':
            text = '&lt;'
        elif text == '&':
            text = '&amp;'

        outfile.write('<symbol> ')
        outfile.write(text)
        outfile.write(' </symbol>' + NEWLINE)



class CompilationEngine:
    pass



def process_jack_file(path):
    '''parses input file'''

    tokenizer_output_path = '.'.join(path.split('.')[:-1]) + 'T.xml'
    tokenizer = JackTokenizer(path, tokenizer_output_path)

    compilation_output_path = '.'.join(path.split('.')[:-1]) + '.xml'
    compilation_engine = CompilationEngine(compilation_output_path, tokenizer)


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

        process_jack_file(input_path)

    elif os.path.isdir(input_path):
        for i in os.listdir(input_path):
            if i.endswith('.jack'):
                process_jack_file(os.path.join(input_path, i))

    else:
        print('enter either a file or folder')

main()
