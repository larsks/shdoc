import argparse
import contextlib
import jinja2
import markdown
import os
import pkg_resources
import sys
from cgi import escape

from shdoc.parser import HashCommentParser

# The default template is included in the package.  This template
# is really meant as an example; a more fully featured template might
# include things like javascript-enabled syntax coloring, or theme
# integration into a larger site, etc.
default_template = pkg_resources.resource_filename(
    __name__,
    'data/template.html.j2')


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--template', '-t',
                   default=default_template,
                   help='Path to the HTML template')
    p.add_argument('--title', '-T',
                   help='Document title (available to template as "title")')
    p.add_argument('--shortname', '-S',
                   action='store_true',
                   help='Use basename rather than full path for title')
    p.add_argument('--output', '-o')
    p.add_argument('--language', '-l',
                   help='Value for "language" key if no '
                   'extension mapping is available')
    p.add_argument('--map-extension', '-m',
                   action='append',
                   default=[],
                   type=lambda x: x.split('=', 1),
                   help='Map file extensions to values for '
                   'the "language" key')
    p.add_argument('--metadata', '-d',
                   action='append',
                   default=[],
                   type=lambda x: x.split('=', 1),
                   help='arbitrary key=value metadata that will be passed '
                        'to the template')

    p.add_argument('input', nargs='?')

    return p.parse_args()


# Make handling i/o using either stdin/stdout or named files
# easier.  Called as `file_or_stdio('myfile', 'w')` it will
# open `myfile` and return a file object, and will close it when
# leaving the context.  Called as `file_or_stdio(None, 'w')` will
# simply return `stdout` (and similar with `stdin` for mode `r`).
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


# Takes a `(code, doc)` chunk from the parser and emits the
# appropriate HTML structure.  Note that for a side-by-side display
# this will require the support of CSS in your template.
def emit_chunk(code, doc):
    return '\n'.join([
        '<div class="outer">',
        '<div class="doc">',
        markdown.markdown('\n'.join(doc)),
        '</div>',
        '<div class="code">',
        '<pre><code>',
        ''.join(escape(x) for x in code),
        '</code></pre>',
        '</div>',
        '</div>',
    ])


def main():
    args = parse_args()
    args.map_extension = dict(args.map_extension)
    args.metadata = dict(args.metadata)

    with open(args.template) as fd:
        template = jinja2.Template(fd.read())

    content = ''
    with file_or_stdio(args.input, 'r') as fd:
        # Set the title to the value of the `--title` option, if
        # provided, otherwise the base filename if `--shortname` was
        # provided, or the full path otherwise.
        title = (args.title if args.title else (
            os.path.basename(fd.name) if args.shortname
            else fd.name))

        # Try to match the file extension against the extension map
        # and set the "language" key.  The "language" key is available
        # to your template and can be used, for example, to explicitly
        # enable syntax highlighting if you are using something like
        # [highlight.js][] or [prism][].
        #
        # [highlight.js]: https://highlightjs.org/
        # [prism]: http://prismjs.com/
        for ext, lname in args.map_extension.items():
            if fd.name.endswith(ext):
                args.language = lname
                break

        for code, doc in HashCommentParser(fd):
            content += emit_chunk(code, doc)

    # Render the template
    with file_or_stdio(args.output, 'w') as fd:
        fd.write(template.render(content=content,
                                 title=title,
                                 language=args.language,
                                 metadata=args.metadata))

if __name__ == '__main__':
    main()
