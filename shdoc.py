import os
import sys
import argparse
import contextlib
import markdown
import jinja2


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--template', '-t',
                   default='template.html')
    p.add_argument('--stylesheet', '-s',
                   default='style.css')
    p.add_argument('--title', '-T')
    p.add_argument('--shortname', '-S',
                   action='store_true')

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


def emit_chunk(chunk, doc):
    return '\n'.join([
        '<div class="outer">',
        '<div class="doc">',
        markdown.markdown('\n'.join(doc)),
        '</div>',
        '<div class="code">',
        '<pre><code>',
        ''.join(chunk),
        '</code></pre>',
        '</div>',
        '</div>',
    ])


def main():
    args = parse_args()

    lineno = 0
    docblocks = {}
    curdoc = []
    code = []

    with open('template.html') as fd:
        template = jinja2.Template(fd.read())

    with file_or_stdin(args.input) as fd:
        title = (args.title if args.title else (
            os.path.basename(fd.name) if args.shortname
            else fd.name))

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

    chunk = []
    doc = []
    content = ''

    for lineno, line in enumerate(code):
        if lineno in docblocks:
            if chunk:
                content += emit_chunk(chunk, doc)
                chunk = []
                doc = []

            doc = docblocks[lineno]

        chunk.append(line)

    if chunk:
        content += emit_chunk(chunk, doc)

    print template.render(content=content,
                          title=title,
                          stylesheet=args.stylesheet)

if __name__ == '__main__':
    main()
