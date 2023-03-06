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

operator_conversion = {'+':'add', '-':'sub', '&':'and', '|':'or', '<':'lt', '>':'gt', '=':'eq'}