import Constants

class JackTokenizer:
    '''
    generates tokens from input file
    allows sequential access to tokens
    '''

    def __init__(self, input_path):
        self.tokens = []
        self.current_pos = -1

        self._create_tokens(input_path)


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


    def _create_tokens(self, input_path):
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

        for i in filtered_lines:
            self._add_line_tokens(i)



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


    def _add_line_tokens(self, line):
        '''
        generates, adds tokens from line of input file
        '''

        quote = False
        text = ''

        for i in line:
            if quote:
                if i == "\"":
                    self._add_string_constant_token(text)
                    quote = False
                    text = ''
                else:
                    text += i

            elif i == "\"":
                quote = True

            elif i in Constants.symbols:
                if len(text) > 0:
                    self._add_uncertain_token(text)
                    text = ''
                self._add_symbol_token(i)

            elif i == ' ':
                if len(text) > 0:
                    self._add_uncertain_token(text)
                    text = ''

            else:
                text += i

        if len(text) > 0:
            self._add_uncertain_token(text)


    def _add_uncertain_token(self, text):
        '''determines token type, adds token to tokens list'''
        if text in Constants.keywords:
            self._add_keyword_token(text)
        elif text.isnumeric():
            self._add_integer_constant_token(text)
        else:
            self._add_identifier_token(text)


    def _add_integer_constant_token(self, text):
        '''adds integer constant to tokens list'''
        self.tokens.append([Constants.INTEGER_CONSTANT, text])


    def _add_string_constant_token(self, text):
        '''adds string constant to tokens list'''
        self.tokens.append([Constants.STRING_CONSTANT, text])


    def _add_keyword_token(self, text):
        '''adds keyword to tokens list'''
        self.tokens.append([Constants.KEYWORD, text])


    def _add_identifier_token(self, text):
        '''adds identifier to tokens list'''
        self.tokens.append([Constants.IDENTIFIER, text])


    def _add_symbol_token(self, text):
        '''adds symbol to tokens list'''
        self.tokens.append([Constants.SYMBOL, text])
