import sys
import read
import symbols
import translate

def main():
    try:
        filename = sys.argv[1]
    except IndexError:
        print('Enter filename')

    lines = read.get_lines(filename)
    no_symbols_lines = symbols.main(lines)
    binary_lines = translate.translate_lines(no_symbols_lines)

    for i in binary_lines:
        print(i)


main()
