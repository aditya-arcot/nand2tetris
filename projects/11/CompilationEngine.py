from SymbolTable import SymbolTable
from VMWriter import VMWriter
import Constants

class CompilationEngine:
    '''generates compiled VM code from Jack tokens'''

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.current_token = ('none', -1)

        self.output_lines = []

        self.class_name = ''
        self.rule_stack = []
        self.if_counter = 0
        self.while_counter = 0

        self.indent = ''

        self.symbol_table = SymbolTable()
        self.vm_writer = VMWriter(self.output_lines)


    def compile(self, output_path):
        '''compiles Jack file containing 1 class, writes to file'''

        self._compile_class()
        self._write(output_path)


    def _advance(self):
        '''advances tokenizer'''
        if self.tokenizer.has_more_tokens():
            self.current_token = self.tokenizer.advance()
        else:
            raise Exception('no more tokens')


    def _current_token_type(self):
        '''get type of current token'''
        return self.current_token[0]


    def _current_token_value(self):
        '''gets value of current token'''
        return self.current_token[1]


    def _next_token_value(self):
        '''gets value of next token'''
        return self.tokenizer.peek()[1]


    def _increase_indent(self):
        '''increases indentation by 2 spaces'''
        self.indent += '  '


    def _decrease_indent(self):
        '''decreases indentation by 2 spaces'''
        self.indent = ' ' * (len(self.indent) - 2)


    def _var_exists(self, name):
        '''checks if variable exists in symbol table'''
        if self.symbol_table.index_of(name) == -1:
            return False
        return True


    def _write(self, output_path):
        '''writes VM code to output file'''
        with open(output_path, 'w', encoding='utf-8') as file:
            for line in self.output_lines:
                file.write(line + Constants.NEWLINE)


    def _compile_class(self):
        """ class: 'class' className '{' classVarDec* subroutineDec* '}' """

        # 'class'
        self._advance()
        # className
        self._advance()
        self.class_name = self.current_token[1]
        # '{'
        self._advance()

        # classVarDec*
        while self._next_token_value() in ('static', 'field'):
            self._compile_class_var_dec()

        # subroutineDec*
        while self._next_token_value() in ('constructor', 'function', 'method'):
            self._compile_subroutine_dec()

        # '}'
        self._advance()


    def _compile_class_var_dec(self):
        """ classVarDec: ('static' | 'field') type varName (',' varName)* ';' """

        # ('static' | 'field')
        self._advance()
        var_kind = self.current_token[1]

        # type
        self._advance()
        var_type = self.current_token[1]

        # varName
        self._advance()
        var_name = self.current_token[1]

        self.symbol_table.define(var_name, var_type, var_kind)

        while self._next_token_value() == ',':
            # (',' varName)*
            for _ in range(2):
                self._advance()

            var_name = self.current_token[1]
            self.symbol_table.define(var_name, var_type, var_kind)

        # ';'
        self._advance()


    def _compile_subroutine_dec(self):
        """ subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
                            subroutineName '(' parameterList ')' subroutineBody """

        # clear subroutine symbol table
        self.symbol_table.start_subroutine()

        # ('constructor' | 'function' | 'method')
        self._advance()
        subroutine_type = self.current_token[1]

        # ('void' | type) subroutineName
        for _ in range(2):
            self._advance()
        subroutine_name = f'{self.class_name}.{self.current_token[1]}'

        # '('
        self._advance()

        # parameterList
        self._compile_parameter_list(subroutine_type)

        # ')'
        self._advance()

        # subroutineBody
        self._compile_subroutine_body(subroutine_name, subroutine_type)

        #self.symbol_table.print_tables()


    def _compile_parameter_list(self, subroutine_type):
        """ parameterList: ((type varName) (',' type varName)*)? """

        if subroutine_type == 'method':
            self.symbol_table.define('this', self.class_name, 'argument')

        while self._next_token_value() != ')':
            # type
            self._advance()
            var_type = self.current_token[1]

            # varName
            self._advance()
            var_name = self.current_token[1]

            self.symbol_table.define(var_name, var_type, 'argument')

            # ','
            if self._next_token_value() == ',':
                self._advance()


    def _compile_subroutine_body(self, subroutine_name, subroutine_type):
        """ subroutineBody: '{' varDec* statements '}' """

        # '{'
        self._advance()

        # varDec*
        while self._next_token_value() == 'var':
            self._compile_var_dec()

        n_local = self.symbol_table.next_local_ind
        self.vm_writer.write_function(subroutine_name, n_local)

        if subroutine_type == 'constructor':
            n_fields = self.symbol_table.next_field_ind
            self.vm_writer.write_push('constant', n_fields)
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop('pointer', 0)
        elif subroutine_type == 'method':
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)

        # statements
        self._compile_statements()

        # '}'
        self._advance()


    def _compile_var_dec(self):
        """ varDec: 'var' type varName (',' varName)* ';' """

        # 'var'
        self._advance()

        # type
        self._advance()
        var_type = self.current_token[1]

        # varName
        self._advance()
        var_name = self.current_token[1]

        self.symbol_table.define(var_name, var_type, 'local')

        while self._next_token_value() != ';':
            # (',' varName)*
            for _ in range(2):
                self._advance()

            var_name = self.current_token[1]
            self.symbol_table.define(var_name, var_type, 'local')

        # ';'
        self._advance()


    def _compile_statements(self):
        """ statements: statement* """

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


    def _compile_let_statement(self):
        """ letStatement: 'let' varName ('[' expression ']')? '=' expression ';' """

        # 'let' varName
        for _ in range(2):
            self._advance()

        var_name = self.current_token[1]
        var_kind = self.symbol_table.kind_of(var_name)
        var_ind = self.symbol_table.index_of(var_name)

        if self._next_token_value() == '[':
            # '['
            self._advance()
            # expression
            self._compile_expression()

            self.vm_writer.write_push(var_kind, var_ind)
            self.vm_writer.write_arithmetic('add')

            # ']'
            self._advance()
            # '='
            self._advance()
            # expression
            self._compile_expression()

            self.vm_writer.write_pop('temp', 0)
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('temp', 0)
            self.vm_writer.write_pop('that', 0)

        else:
            # '='
            self._advance()
            # expression
            self._compile_expression()

            self.vm_writer.write_pop(var_kind, var_ind)

        # ';'
        self._advance()


    def _compile_if_statement(self):
        """ ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')? """

        # 'if' '('
        for _ in range(2):
            self._advance()

        self._compile_expression()

        true_label = f'IF_TRUE_{self.if_counter}'
        false_label = f'IF_FALSE_{self.if_counter}'
        end_label = f'IF_END_{self.if_counter}'
        self.if_counter += 1
        self.vm_writer.write_if(true_label)
        self.vm_writer.write_goto(false_label)

        # ')' '{'
        for _ in range(2):
            self._advance()

        self.vm_writer.write_label(true_label)
        self._compile_statements()
        self.vm_writer.write_goto(end_label)

        # '}'
        self._advance()

        self.vm_writer.write_label(false_label)
        if self._next_token_value() == 'else':
            # 'else' '{'
            for _ in range(2):
                self._advance()
            # statements
            self._compile_statements()
            # '}'
            self._advance()

        self.vm_writer.write_label(end_label)


    def _compile_while_statement(self):
        """ whileStatement: 'while' '(' expression ')' '{' statements '}' """

        # 'while' '('
        for _ in range(2):
            self._advance()

        true_label = f'WHILE_TRUE_{self.while_counter}'
        end_label = f'WHILE_END_{self.while_counter}'
        self.while_counter += 1
        self.vm_writer.write_label(true_label)

        self._compile_expression()
        self.vm_writer.write_arithmetic('not')
        self.vm_writer.write_if(end_label)

        # ')' '{'
        for _ in range(2):
            self._advance()

        self._compile_statements()
        self.vm_writer.write_goto(true_label)

        # '}'
        self._advance()

        self.vm_writer.write_label(end_label)


    def _compile_do_statement(self):
        """ doStatement: 'do' subroutineCall ';' """

        # 'do'
        self._advance()

        # subroutineCall
        self._advance()
        self._compile_subroutine_call()

        self.vm_writer.write_pop('temp', 0) # discard void value

        # ';'
        self._advance()


    def _compile_subroutine_call(self):
        """ subroutineCall: subroutineName '(' expressionList ')' | (className | varName) '.'
                                subroutineName '(' expressionList ')' """

        # subroutineName | (className | varName)
        start_token = self.current_token

        n_args = 0

        if self._next_token_value() == '.':
            # '.'
            self._advance()
            # subroutineName
            self._advance()

            if self._var_exists(start_token[1]): # instance
                var_name = start_token[1]
                var_type = self.symbol_table.type_of(var_name)
                var_kind = self.symbol_table.kind_of(var_name)
                var_ind = self.symbol_table.index_of(var_name)
                self.vm_writer.write_push(var_kind, var_ind)
                func_name = f'{var_type}.{self.current_token[1]}'
                n_args = 1
            else: # class
                func_name = f'{start_token[1]}.{self.current_token[1]}'

        else: # next is (
            self.vm_writer.write_push('pointer', 0)
            func_name = f'{self.class_name}.{start_token[1]}'
            n_args = 1

        # '('
        self._advance()
        # expressionList
        n_args += self._compile_expression_list()
        # ')'
        self._advance()

        self.vm_writer.write_call(func_name, n_args)


    def _compile_return_statement(self):
        """ returnStatement: 'return' expression? ';' """

        # 'return'
        self._advance()

        if self._next_token_value() != ';':
            self._compile_expression()
        else:
            self.vm_writer.write_push('constant', 0)

        self.vm_writer.write_return()

        # ';'
        self._advance()


    def _compile_expression(self):
        """ expression: term (op term)* """

        # term
        self._compile_term()

        while self._next_token_value() in Constants.operators:
            # op term
            self._advance()
            operator = self.current_token[1]
            self._compile_term()

            if operator == '*':
                self.vm_writer.write_call('Math.multiply', 2)
            elif operator == '/':
                self.vm_writer.write_call('Math.divide', 2)
            elif operator in Constants.operator_conversion:
                self.vm_writer.write_arithmetic(Constants.operator_conversion[operator])


    def _compile_term(self):
        """ term: integerConstant | stringConstant | keywordConstant | varName |
		            varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp
		            term """

        self._advance()

        cur_type = self._current_token_type()
        cur_val = self._current_token_value()

        # stringConstant
        if cur_type == Constants.STRING_CONSTANT:
            self._compile_string()

        # integerConstant
        elif cur_type == Constants.INTEGER_CONSTANT:
            self.vm_writer.write_push('constant', int(self.current_token[1]))

        # keywordConstant
        elif cur_val in Constants.keyword_constants:
            if cur_val in ('true', 'false', 'null'):
                self.vm_writer.write_push('constant', 0)
                if cur_val == 'true':
                    self.vm_writer.write_arithmetic('not')
            else: # this
                self.vm_writer.write_push('pointer', 0)

        # varName | varName '[' expression ']' | subroutineCall
        # varName | subroutineName | className
        elif cur_type == Constants.IDENTIFIER:
            # '[' expression ']'
            if self._next_token_value() == '[':
                self._advance()
                self._compile_expression()
                self._advance()

                var_kind = self.symbol_table.kind_of(cur_val)
                var_ind = self.symbol_table.index_of(cur_val)
                self.vm_writer.write_push(var_kind, var_ind)
                self.vm_writer.write_arithmetic('add')
                self.vm_writer.write_pop('pointer', 1)
                self.vm_writer.write_push('that', 0)

            # subroutineCall
            elif (self._next_token_value() == '(') | (self._next_token_value() == '.'):
                self._compile_subroutine_call()

            # varName
            else:
                var_kind = self.symbol_table.kind_of(cur_val)
                var_ind = self.symbol_table.index_of(cur_val)
                self.vm_writer.write_push(var_kind, var_ind)

        # '(' expression ')'
        elif cur_val == '(':
            self._compile_expression()
            # ')'
            self._advance()

        # unaryOp term
        elif cur_val in Constants.unary_operators:
            self._compile_term()
            if cur_val == '-':
                self.vm_writer.write_arithmetic('neg')
            else: # ~
                self.vm_writer.write_arithmetic('not')


    def _compile_string(self):
        '''compiles string 1 character at a time'''
        string = self.current_token[1]

        self.vm_writer.write_push('constant', len(string))
        self.vm_writer.write_call('String.new', 1)

        for letter in string:
            self.vm_writer.write_push('constant', ord(letter))
            self.vm_writer.write_call('String.appendChar', 2)


    def _compile_expression_list(self):
        """ expressionList: (expression (',' expression)*)? """

        n_args = 0

        while self._next_token_value() != ')':
            # expression
            self._compile_expression()
            n_args += 1

            if self._next_token_value() == ',':
                self._advance()

        return n_args
