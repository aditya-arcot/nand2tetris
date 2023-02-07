# get lines of program
# includes A instructions, C instructions, label declarations
def get_lines(filename):
    # store lines of program
    lines = []

    # open file
    with open(filename, 'r') as infile:
        # iterate over lines
        for line in infile:
            # discard whitespace, newline
            line = line.replace(' ', '').strip()

            # discard blank lines, comments
            if (not line == "") and (not line.startswith('//')):
                # discard end-of-line comments
                lines.append(line.split('//')[0])

    return lines
