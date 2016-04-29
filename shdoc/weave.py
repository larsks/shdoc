import argparse

from shdoc.parser import HashCommentParser
from shdoc.util import file_or_stdio


def parse_args():
    p = argparse.ArgumentParser()

    # `--output OUTPUT`
    #
    # Send output to a file, rather than to *stdout*.
    p.add_argument('--output', '-o')

    p.add_argument('input', nargs='?')

    return p.parse_args()


def main():
    args = parse_args()

    with file_or_stdio(args.input, 'r') as infd, \
            file_or_stdio(args.output, 'w') as outfd:

        for code, doc in HashCommentParser(infd):
            outfd.write(''.join(doc))
            outfd.write('\n')


if __name__ == '__main__':
    main()
