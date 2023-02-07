def translate_lines(lines):
    out = []
    for line in lines:
        if line.startswith('@'):    # A instruction
            out.append(A_instruction_binary(line))

        else:                       # C instruction
            out.append(C_instruction_binary(line))

    return out


# accepts positive integers
def convert_to_binary(n):
    if type(n) != int:
        raise Exception('not an integer')
    if n < 0:
        raise Exception('not a positive integer')
    if n == 0:
        return '0'

    out = ''
    while n > 0:
        out = str(n%2) + out
        n //= 2

    return out


def pad(st, l, ch='0'):
    while len(st) < l:
        st = ch + st
    return st



def A_instruction_binary(line):
    value = int(line[1:])
    binary_value = convert_to_binary(value)
    padded_binary_value = pad(binary_value, 15)
    return '0' + padded_binary_value # add op code


def C_instruction_binary(line):
    out = ''

    split = line.split(';')
    if len(split) > 1: # jump statement exists
        out += jump_binary(split[1])
    else:
        out += '000'

    split = split[0].split('=')
    if len(split) > 1: # dest statement exists
        out = dest_binary(split[0]) + out
        out = comp_binary(split[1]) + out
    else:
        out = '000' + out
        out = comp_binary(split[0]) + out

    return '111' + out

comp_dict = {
'0':'0101010',
'1':'0111111',
'-1':'0111010',
'D':'0001100',
'A':'0110000',
'M':'1110000',
'!D':'0001101',
'!A':'0110001',
'!M':'1110001',
'-D':'0001111',
'-A':'0110011',
'-M':'1110011',
'D+1':'0011111',
'A+1':'0110111',
'M+1':'1110111',
'D-1':'0001110',
'A-1':'0110010',
'M-1':'1110010',
'D+A':'0000010',
'D+M':'1000010',
'D-A':'0010011',
'D-M':'1010011',
'A-D':'0000111',
'M-D':'1000111',
'D&A':'0000000',
'D&M':'1000000',
'D|A':'0010101',
'D|M':'1010101'
}
def comp_binary(st):
    if st not in comp_dict:
        raise Exception('unknown comp')
    return comp_dict[st]


dest_dict = {
'M':'001',
'D':'010',
'MD':'011',
'A':'100',
'AM':'101',
'AD':'110',
'AMD':'111'
}
def dest_binary(st):
    if st not in dest_dict:
        raise Exception('unknown dest')
    return dest_dict[st]


jump_dict = {
'JGT':'001',
'JEQ':'010',
'JGE':'011',
'JLT':'100',
'JNE':'101',
'JLE':'110',
'JMP':'111'
}
def jump_binary(st):
    if st not in jump_dict:
        raise Exception('unknown jump')
    return jump_dict[st]
