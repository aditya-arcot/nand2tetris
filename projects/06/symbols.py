symbols_dict = {
'R0':'0',
'R1':'1',
'R2':'2',
'R3':'3',
'R4':'4',
'R5':'5',
'R6':'6',
'R7':'7',
'R8':'8',
'R9':'9',
'R10':'10',
'R11':'11',
'R12':'12',
'R13':'13',
'R14':'14',
'R15':'15',
'SCREEN':'16384',
'KBD':'24576',
'SP':'0',
'LCL':'1',
'ARG':'2',
'THIS':'3',
'THAT':'4'
}

def main(lines):
    filtered_lines = pass_1(lines)
    pass_2(filtered_lines)
    return filtered_lines


# populate labels
# delete declaration lines
def pass_1(lines):
    filtered_lines = []
    for line in lines:
        if line.startswith('('):
            label = line[1:-1]
            symbols_dict[label] = len(filtered_lines)
        else:
            filtered_lines.append(line)
    return filtered_lines


# add new variables
# substitute variables, labels
def pass_2(lines):
    next_available_register = 16

    for i in range(len(lines)):
        line = lines[i]
        if line.startswith('@'):
            symbol = line[1:]
            try:
                int(symbol)
                continue
            except ValueError: # variable, not number
                pass

            if symbol not in symbols_dict:
                symbols_dict[symbol] = next_available_register
                next_available_register += 1

            # replace
            line = '@' + str(symbols_dict[symbol])
            lines[i] = line
