from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
import Constants

class CompilationEngine:
    '''
    parses tokens
    generates XML parse tree
    '''
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
        if self._current_token_type() == Constants.KEYWORD:
            self._append_output('<keyword> ' + self._current_token_value() + ' </keyword>')
        elif self._current_token_type() == Constants.SYMBOL:
            val = self._current_token_value()
            if val == '>':
                self._append_output('<symbol> &gt; </symbol>')
            elif val == '<':
                self._append_output('<symbol> &lt; </symbol>')
            elif val == '&':
                self._append_output('<symbol> &amp; </symbol>')
            else:
                self._append_output('<symbol> ' + self._current_token_value() + ' </symbol>')
        elif self._current_token_type() == Constants.INTEGER_CONSTANT:
            self._append_output('<integerConstant> ' + self._current_token_value() +
                                ' </integerConstant>')
        elif self._current_token_type() == Constants.STRING_CONSTANT:
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


    def print_lines(self):
        '''print output lines'''
        for line in self.output_lines:
        #if 'identifier' in line: 
            print(line)


    def compile(self, tokenizer):
        '''compiles jack file containing 1 class, writes to file'''
        self.current_token = ('none', -1)
        self.tokenizer = tokenizer
        self.indent = ''
        self.output_lines = []
        self.rule_stack = []
        self.class_name = ''
        self.symbol_table = SymbolTable()

        self._compile_class()


    def _compile_class(self):
        """ class: 'class' className '{' classVarDec* subroutineDec* '}' """

        self._append_non_terminal_start('class')

        # 'class' 
        self._advance()
        # className 
        self._advance()
        self._class_dec()
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

        self._append_non_terminal_end()

    
    def _compile_class_var_dec(self):
        """ classVarDec: ('static' | 'field') type varName (',' varName)* ';' """

        self._append_non_terminal_start('classVarDec')

        # ('static' | 'field') 
        self._advance()
        var_kind = self.current_token[1]

        # type
        self._advance()
        var_type = self.current_token[1]
        
        # varName
        self._advance()
        var_name = self.current_token[1]

        self._var_dec(var_name, var_type, var_kind)

        while self._next_token_value() == ',':
            # (',' varName)*
            for _ in range(2):
                self._advance()
            
            var_name = self.current_token[1]
            self._var_dec(var_name, var_type, var_kind)

        # ';'
        self._advance()

        self._append_non_terminal_end()


    def _compile_subroutine_dec(self):
        """ subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
                            subroutineName '(' parameterList ')' subroutineBody """

        # clear subroutine symbol table
        self.symbol_table.start_subroutine() 

        self._append_non_terminal_start('subroutineDec')

        # ('constructor' | 'function' | 'method') 
        self._advance()
        method = self.current_token[1] == 'method'
        
        # ('void' | type) subroutineName
        for _ in range(2):
            self._advance()
        self._subroutine_dec(method)

        # '('
        self._advance()

        # parameterList
        self._compile_parameter_list()

        # ')'
        self._advance()

        # subroutineBody
        self._compile_subroutine_body()

        self._append_non_terminal_end()
        
        self.symbol_table.print_tables()


    def _compile_parameter_list(self):
        """ parameterList: ((type varName) (',' type varName)*)? """

        self._append_non_terminal_start('parameterList')

        while self._next_token_value() != ')':
            # type
            self._advance()
            var_type = self.current_token[1]
            
            # varName
            self._advance()
            var_name = self.current_token[1]

            self._var_dec(var_name, var_type, 'argument')

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

        # 'var'
        self._advance()
        
        # type
        self._advance()
        var_type = self.current_token[1]
        
        # varName
        self._advance()
        var_name = self.current_token[1]

        self._var_dec(var_name, var_type, 'local')

        while self._next_token_value() != ';':
            # (',' varName)*
            for _ in range(2):
                self._advance()
            
            var_name = self.current_token[1]
            self._var_dec(var_name, var_type, 'local')

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
        self._var_access()
        
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

        # TODO
        """ subroutineCall: subroutineName '(' expressionList ')' | (className | varName) '.'
                                subroutineName '(' expressionList ')' """
        # subroutineName | (className | varName)
        self._advance()
        if self._next_token_value() == '.':
            if self.var_exists(self.current_token[1]):
                self._var_access()
            else:
                self._class_access()

            # '.'
            self._advance()
            # subroutineName
            self._advance()
        
        self._subroutine_access()

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

        while self._next_token_value() in Constants.operators:
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
        if next_type in (Constants.INTEGER_CONSTANT, Constants.STRING_CONSTANT) or \
                next_val in Constants.keyword_constants:
            self._advance()

        # varName | varName '[' expression ']' | subroutineCall
        elif next_type == Constants.IDENTIFIER:
            # varName | subroutineName | className
            self._advance()

            # current -> varName
            # '[' expression ']'
            if self._next_token_value() == '[':
                self._var_access()

                self._advance()
                self._compile_expression()
                self._advance()

            # current -> subroutineName
            # '(' expressionList ')'
            elif self._next_token_value() == '(':
                self._subroutine_access()

                self._advance()
                self._compile_expression_list()
                self._advance()

            # current -> (className | varName)
            # '.' subroutineName '(' expressionList ')'
            elif self._next_token_value() == '.':
                if self.var_exists(self.current_token[1]):
                    self._var_access()
                else:
                    self._class_access()

                for _ in range(2):
                    self._advance()
                self._subroutine_access()
                self._advance()

                self._compile_expression_list()
                self._advance()

            else:
                self._var_access()

        # '(' expression ')'
        elif next_val == '(':
            self._advance()
            self._compile_expression()
            self._advance()

        # unaryOp term
        elif next_val in Constants.unary_operators:
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



    def var_exists(self, name):
        if self.symbol_table.index_of(name) == -1:
            return False
        return True

    def _var_access(self):
        var_name = self.current_token[1]
        var_type = self.symbol_table.type_of(var_name)
        var_kind = self.symbol_table.kind_of(var_name)
        var_ind = self.symbol_table.index_of(var_name)
        print(f'var acc\t{var_name}\t{var_type}\t{var_kind}\t{var_ind}')

    def _subroutine_access(self):
        print(f'sub acc\t{self.current_token[1]}')

    def _class_access(self):
        print(f'cls acc\t{self.current_token[1]}')

    def _var_dec(self, var_name, var_type, var_kind):
        self.symbol_table.define(var_name, var_type, var_kind)
        print(f'var dec\t{var_name}\t{var_type}\t{var_kind}\t{self.symbol_table.index_of(var_name)}')

    def _subroutine_dec(self, method):
        print(f'sub dec - {self.current_token[1]}')
        if method:
            self._var_dec('this', self.class_name, 'argument')

    def _class_dec(self):
        self.class_name = self.current_token[1]
        print(f'cls dec - {self.class_name}')

