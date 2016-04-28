import sys
import argparse
import contextlib


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('input', nargs='?')

    return p.parse_args()


@contextlib.contextmanager
def file_or_stdin(name):
    if name is None:
        fd = sys.stdin
    else:
        fd = open(name, 'r')

    yield fd

    if fd is not sys.stdin:
        fd.close()


def main():
    args = parse_args()

    lineno = 0
    docblocks = {}
    curdoc = []
    code = []

    with file_or_stdin(args.input) as fd:
        for line in fd:
            if line.startswith('# ') or line.strip() == '#':
                curdoc.append(line.strip()[2:])
            else:
                if curdoc:
                    docblocks[lineno] = curdoc
                    curdoc = []
                code.append(line)
                lineno += 1

        if curdoc:
            docblocks[lineno] = curdoc

    incode = False
    indiv = False

    for lineno, line in enumerate(code):
        if lineno in docblocks:
            if incode:
                sys.stdout.write('</code></pre>\n')
                incode = False
            sys.stdout.write('<div class="doc" markdown="1">')
            sys.stdout.write('\n'.join(docblocks[lineno]))
            sys.stdout.write('\n')
            sys.stdout.write('</div>\n')
            sys.stdout.write('\n')

        if not incode:
            sys.stdout.write('<pre class="code"><code>\n')
            incode = True
        sys.stdout.write(line)

    if incode:
        sys.stdout.write('</code></pre>\n')

if __name__ == '__main__':
    main()
