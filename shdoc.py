import argparse
import contextlib
import jinja2
import markdown
import os
import sys
from cgi import escape

from documenter import Documenter


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--template', '-t',
                   default='template.html')
    p.add_argument('--stylesheet', '-s',
                   default='style.css')
    p.add_argument('--title', '-T')
    p.add_argument('--shortname', '-S',
                   action='store_true')
    p.add_argument('--output', '-o')
    p.add_argument('--language', '-l')
    p.add_argument('--map-extension', '-m',
                   action='append',
                   default=[],
                   type=lambda x: x.split('=', 1))

    p.add_argument('input', nargs='?')

    return p.parse_args()


@contextlib.contextmanager
def file_or_stdio(name, mode):
    if name is None:
        if mode == 'r':
            fd = sys.stdin
        elif mode == 'w':
            fd = sys.stdout
        else:
            raise ValueError('mode must be "r" or "w" for stdio')
    else:
        fd = open(name, mode)

    yield fd

    if fd not in [sys.stdin, sys.stdout]:
        fd.close()


def emit_chunk(chunk, doc):
    return '\n'.join([
        '<div class="outer">',
        '<div class="doc">',
        markdown.markdown('\n'.join(doc)),
        '</div>',
        '<div class="code">',
        '<pre><code>',
        ''.join(escape(x) for x in chunk),
        '</code></pre>',
        '</div>',
        '</div>',
    ])


def main():
    args = parse_args()
    args.map_extension = dict(args.map_extension)

    with open(args.template) as fd:
        template = jinja2.Template(fd.read())

    content = ''
    with file_or_stdio(args.input, 'r') as fd:
        title = (args.title if args.title else (
            os.path.basename(fd.name) if args.shortname
            else fd.name))

        for ext, lname in args.map_extension.items():
            if fd.name.endswith(ext):
                args.language = lname
                break

        for code, doc in Documenter(fd):
            content += emit_chunk(code, doc)

    with file_or_stdio(args.output, 'w') as fd:
        fd.write(template.render(content=content,
                                 title=title,
                                 language=args.language,
                                 stylesheet=args.stylesheet))

if __name__ == '__main__':
    main()
