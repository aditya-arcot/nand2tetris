'''part 1 of compiler - tokenizer and parser generate XML to be used by code generator'''

import os
import sys
import time

NEWLINE = '\n'

KEYWORD = 0
SYMBOL = 1
INTEGER_CONSTANT = 2
STRING_CONSTANT = 3
IDENTIFIER = 4

keywords = ['class', 'constructor', 'function', 'method', 'field', 'static',
            'var', 'int', 'char','boolean', 'void', 'true', 'false', 'null',
            'this', 'let', 'do', 'if', 'else', 'while', 'return']
symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', \
            '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

operators = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
unary_operators = ['-', '~']
keyword_constants = ['true', 'false', 'null', 'this']


class JackTokenizer:
    '''
    generates tokens from input file
    allows sequential access to tokens
    '''

    def __init__(self, input_path, output_path):
        self.tokens = []
        self.current_pos = -1

        self._create_tokens(input_path, output_path)


    def has_more_tokens(self):
        '''checks if more tokens exist'''
        if self.current_pos == len(self.tokens) - 1:
            return False
        return True


    def advance(self):
        '''advances to next token, returns it'''
        self.current_pos += 1
        return self.tokens[self.current_pos]


    def peek(self):
        '''returns next token'''
        if self.has_more_tokens():
            return self.tokens[self.current_pos + 1]
        return ('no more tokens', 0)


    def _create_tokens(self, input_path, output_path):
        '''
        splits input file into tokens
        outputs result to tokens list and XML
        '''

        with open(input_path, 'r', encoding='utf8') as infile:
            lines = infile.readlines()

        filtered_lines = []
        # remove comments after //
        for line in lines:
            filtered_lines.append(line.split('//')[0])
        # remove block comments (including multi-line)
        filtered_lines = self._remove_block_comments(filtered_lines)
        # remove empty lines
        filtered_lines = [i.strip() for i in filtered_lines if i.strip() != '']

        with open(output_path, 'w', encoding='utf8') as outfile:
            outfile.write('<tokens>' + NEWLINE)

            for i in filtered_lines:
                self._write_tokens(i, outfile)

            outfile.write('</tokens>' + NEWLINE)


    def _remove_block_comments(self, lines):
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


    def _write_tokens(self, line, outfile):
        '''
        generates, writes tokens from line of input file
        '''

        quote = False
        text = ''

        for i in line:
            if quote:
                if i == "\"":
                    self._write_string_constant(text, outfile)
                    quote = False
                    text = ''
                else:
                    text += i

            elif i == "\"":
                quote = True

            elif i in symbols:
                if len(text) > 0:
                    self._write_uncertain(text, outfile)
                    text = ''
                self._write_symbol(i, outfile)

            elif i == ' ':
                if len(text) > 0:
                    self._write_uncertain(text, outfile)
                    text = ''

            else:
                text += i

        if len(text) > 0:
            self._write_uncertain(text, outfile)


    def _write_uncertain(self, text, outfile):
        '''determines token type, writes token'''
        if text in keywords:
            self._write_keyword(text, outfile)
        elif text.isnumeric():
            self._write_integer_constant(text, outfile)
        else:
            self._write_identifier(text, outfile)


    def _write_integer_constant(self, text, outfile):
        '''writes integer constant to XML, stores in tokens list'''
        self._write_token('integerConstant', text, outfile)
        self.tokens.append([INTEGER_CONSTANT, text])


    def _write_string_constant(self, text, outfile):
        '''writes string constant to XML, stores in tokens list'''
        self._write_token('stringConstant', text, outfile)
        self.tokens.append([STRING_CONSTANT, text])


    def _write_keyword(self, text, outfile):
        '''writes keyword to XML, stores in tokens list'''
        self._write_token('keyword', text, outfile)
        self.tokens.append([KEYWORD, text])


    def _write_identifier(self, text, outfile):
        '''writes identifier to XML, stores in tokens list'''
        self._write_token('identifier', text, outfile)
        self.tokens.append([IDENTIFIER, text])


    def _write_symbol(self, text, outfile):
        '''writes symbol to XML, stores in tokens list'''
        self.tokens.append([SYMBOL, text])

        if text == '>':
            text = '&gt;'
        elif text == '<':
            text = '&lt;'
        elif text == '&':
            text = '&amp;'

        self._write_token('symbol', text, outfile)


    def _write_token(self, type, token, outfile):
        '''writes token and tags to file'''
        outfile.write(f'<{type}> ')
        outfile.write(token)
        outfile.write(f' </{type}>' + NEWLINE)



class CompilationEngine:
    '''
    parses tokens
    generates XML parse tree
    '''
    def __init__(self, output_path, tokenizer: JackTokenizer):
        self.output_path = output_path
        self.current_token = ('none', -1)
        self.tokenizer = tokenizer
        self.indent = ''
        self.output_lines = []
        self.rule_stack = []


    def _advance(self):
        '''advances tokenizer, appends output'''
        if self.tokenizer.has_more_tokens():
            self.current_token = self.tokenizer.advance()
            self._append_terminal_output()
        else:
            raise Exception('no more tokens')


    def _current_token_type(self):
        '''get type of current token'''
        return self.current_token[0]


    def _current_token_value(self):
        '''gets value of current token'''
        return self.current_token[1]


    def _next_token_type(self):
        '''gets type of next token'''
        return self.tokenizer.peek()[0]


    def _next_token_value(self):
        '''gets value of next token'''
        return self.tokenizer.peek()[1]


    def _increase_indent(self):
        '''increases indentation by 2 spaces'''
        self.indent += '  '


    def _decrease_indent(self):
        '''decreases indentation by 2 spaces'''
        self.indent = ' ' * (len(self.indent) - 2)


    def _append_output(self, text):
        '''appends indentation and text to output'''
        self.output_lines.append(self.indent + text)


    def _append_terminal_output(self):
        '''appends terminal tokens to output'''
        if self._current_token_type() == KEYWORD:
            self._append_output('<keyword> ' + self._current_token_value() + ' </keyword>')
        elif self._current_token_type() == SYMBOL:
            val = self._current_token_value()
            if val == '>':
                self._append_output('<symbol> &gt; </symbol>')
            elif val == '<':
                self._append_output('<symbol> &lt; </symbol>')
            elif val == '&':
                self._append_output('<symbol> &amp; </symbol>')
            else:
                self._append_output('<symbol> ' + self._current_token_value() + ' </symbol>')
        elif self._current_token_type() == INTEGER_CONSTANT:
            self._append_output('<integerConstant> ' + self._current_token_value() +
                                ' </integerConstant>')
        elif self._current_token_type() == STRING_CONSTANT:
            self._append_output('<stringConstant> ' + self._current_token_value() +
                                ' </stringConstant>')
        else:
            self._append_output('<identifier> ' + self._current_token_value() + ' </identifier>')


    def _append_non_terminal_start(self, rule):
        '''appends non-terminal tokens start'''
        self._append_output(f'<{rule}>')
        self._increase_indent()
        self.rule_stack.append(rule)


    def _append_non_terminal_end(self):
        '''appends non-terminal tokens end'''
        self._decrease_indent()
        rule = self.rule_stack.pop()
        self._append_output(f'</{rule}>')


    def write_xml(self):
        '''writes output lines to file'''
        with open(self.output_path, 'w', encoding='utf8') as outfile:
            for line in self.output_lines:
                outfile.write(line + NEWLINE)


    def compile(self):
        '''compiles jack file containing 1 class, writes to file'''
        self._compile_class()


    def _compile_class(self):
        """ class: 'class' className '{' classVarDec* subroutineDec* '}' """

        self._append_non_terminal_start('class')

        # 'class' className '{'
        for _ in range(3):
            self._advance()

        # classVarDec*
        while self._next_token_value() in ('static', 'field'):
            self._compile_class_var_dec()

        # subroutineDec*
        while self._next_token_value() in ('constructor', 'function', 'method'):
            self._compile_subroutine_dec()

        # '}'
        self._advance()

        self._append_non_terminal_end()


    def _compile_class_var_dec(self):
        """ classVarDec: ('static' | 'field') type varName (',' varName)* ';' """

        self._append_non_terminal_start('classVarDec')

        # ('static' | 'field') type varName
        for _ in range(3):
            self._advance()

        while self._next_token_value() == ',':
            # (',' varName)*
            for _ in range(2):
                self._advance()

        # ';'
        self._advance()

        self._append_non_terminal_end()


    def _compile_subroutine_dec(self):
        """ subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
                            subroutineName '(' parameterList ')' subroutineBody """

        self._append_non_terminal_start('subroutineDec')

        # ('constructor' | 'function' | 'method') ('void' | type) subroutineName '('
        for _ in range(4):
            self._advance()

        # parameterList
        self._compile_parameter_list()

        # ')'
        self._advance()

        # subroutineBody
        self._compile_subroutine_body()

        self._append_non_terminal_end()


    def _compile_parameter_list(self):
        """ parameterList: ((type varName) (',' type varName)*)? """

        self._append_non_terminal_start('parameterList')

        while self._next_token_value() != ')':
            # type varName
            for _ in range(2):
                self._advance()

            # ','
            if self._next_token_value() == ',':
                self._advance()

        self._append_non_terminal_end()


    def _compile_subroutine_body(self):
        """ subroutineBody: '{' varDec* statements '}' """

        self._append_non_terminal_start('subroutineBody')

        # '{'
        self._advance()

        # varDec*
        while self._next_token_value() == 'var':
            self._compile_var_dec()

        # statements
        self._compile_statements()

        # '}'
        self._advance()

        self._append_non_terminal_end()


    def _compile_var_dec(self):
        """ varDec: 'var' type varName (',' varName)* ';' """

        self._append_non_terminal_start('varDec')

        # 'var' type varName
        for _ in range(3):
            self._advance()

        while self._next_token_value() != ';':
            # (',' varName)*
            for _ in range(2):
                self._advance()

        # ';'
        self._advance()

        self._append_non_terminal_end()


    def _compile_statements(self):
        """ statements: statement* """

        self._append_non_terminal_start('statements')

        next_val = self._next_token_value()
        while next_val != '}':
            # letStatement
            if next_val == 'let':
                self._compile_let_statement()
            # ifStatement
            elif next_val == 'if':
                self._compile_if_statement()
            # whileStatement
            elif next_val == 'while':
                self._compile_while_statement()
            # doStatement
            elif next_val == 'do':
                self._compile_do_statement()
            # returnStatement
            else:
                self._compile_return_statement()

            next_val = self._next_token_value()

        self._append_non_terminal_end()


    def _compile_let_statement(self):
        """ letStatement: 'let' varName ('[' expression ']')? '=' expression ';' """

        self._append_non_terminal_start('letStatement')

        # 'let' varName
        for _ in range(2):
            self._advance()

        if self._next_token_value() == '[':
            # '['
            self._advance()
            self._compile_expression()
            # ']'
            self._advance()

        # '='
        self._advance()

        self._compile_expression()

        # ';'
        self._advance()

        self._append_non_terminal_end()


    def _compile_if_statement(self):
        """ ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')? """

        self._append_non_terminal_start('ifStatement')

        # 'if' '('
        for _ in range(2):
            self._advance()

        self._compile_expression()

        # ')' '{'
        for _ in range(2):
            self._advance()

        self._compile_statements()

        # '}'
        self._advance()

        if self._next_token_value() == 'else':
            # 'else' '{'
            for _ in range(2):
                self._advance()
            # statements
            self._compile_statements()
            # '}'
            self._advance()

        self._append_non_terminal_end()


    def _compile_while_statement(self):
        """ whileStatement: 'while' '(' expression ')' '{' statements '}' """

        self._append_non_terminal_start('whileStatement')

        # 'while' '('
        for _ in range(2):
            self._advance()

        self._compile_expression()

        # ')' '{'
        for _ in range(2):
            self._advance()

        self._compile_statements()

        # '}'
        self._advance()

        self._append_non_terminal_end()


    def _compile_do_statement(self):
        """ doStatement: 'do' subroutineCall ';' """

        self._append_non_terminal_start('doStatement')

        # 'do'
        self._advance()


        """ subroutineCall: subroutineName '(' expressionList ')' | (className | varName) '.'
                                subroutineName '(' expressionList ')' """
        # subroutineName | (className | varName)
        self._advance()
        if self._next_token_value() == '.':
            # '.'
            self._advance()
            # subroutineName
            self._advance()
        
        # '('
        self._advance()
        # expressionList
        self._compile_expression_list()
        # ')'
        self._advance()


        # ';'
        self._advance()

        self._append_non_terminal_end()


    def _compile_return_statement(self):
        """ returnStatement: 'return' expression? ';' """

        self._append_non_terminal_start('returnStatement')

        # 'return'
        self._advance()

        if self._next_token_value() != ';':
            self._compile_expression()

        # ';'
        self._advance()

        self._append_non_terminal_end()


    def _compile_expression(self):
        """ expression: term (op term)* """

        self._append_non_terminal_start('expression')

        # term
        self._compile_term()

        while self._next_token_value() in operators:
            # op term
            self._advance()
            self._compile_term()

        self._append_non_terminal_end()


    def _compile_term(self):
        """ term: integerConstant | stringConstant | keywordConstant | varName |
		            varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp
		            term """

        self._append_non_terminal_start('term')

        next_type = self._next_token_type()
        next_val = self._next_token_value()

        # integerConstant | stringConstant | keywordConstant
        if next_type in (INTEGER_CONSTANT, STRING_CONSTANT) or \
                next_val in keyword_constants:
            self._advance()

        # varName | varName '[' expression ']' | subroutineCall
        elif next_type == IDENTIFIER:
            # varName | subroutineName | className
            self._advance()

            # current -> varName
            # '[' expression ']'
            if self._next_token_value() == '[':
                self._advance()
                self._compile_expression()
                self._advance()

            # current -> subroutineName
            # '(' expressionList ')'
            elif self._next_token_value() == '(':
                self._advance()
                self._compile_expression_list()
                self._advance()
                
            # current -> (className | varName)
            # '.' subroutineName '(' expressionList ')'
            elif self._next_token_value() == '.':
                for _ in range(3):
                    self._advance()
                self._compile_expression_list()
                self._advance()

        # '(' expression ')'
        elif next_val == '(':
            self._advance()
            self._compile_expression()
            self._advance()

        # unaryOp term
        elif next_val in unary_operators:
            self._advance()
            self._compile_term()

        self._append_non_terminal_end()


    def _compile_expression_list(self):
        """ expressionList: (expression (',' expression)*)? """

        self._append_non_terminal_start('expressionList')

        while self._next_token_value() != ')':
            # expression
            self._compile_expression()

            if self._next_token_value() == ',':
                self._advance()

        self._append_non_terminal_end()



def process_jack_file(path):
    '''parses input file'''

    tokenizer_output_path = '.'.join(path.split('.')[:-1]) + 'T.xml'
    tokenizer = JackTokenizer(path, tokenizer_output_path)

    compilation_output_path = '.'.join(path.split('.')[:-1]) + '.xml'
    compilation_engine = CompilationEngine(compilation_output_path, tokenizer)
    compilation_engine.compile()
    compilation_engine.write_xml()


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
