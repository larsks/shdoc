import argparse
import jinja2
import markdown
import os
import pkg_resources
from cgi import escape

from shdoc.parser import HashCommentParser
from shdoc.util import file_or_stdio

# The default template is included in the package.  This template
# is really meant as an example; a more fully featured template might
# include things like javascript-enabled syntax coloring, or theme
# integration into a larger site, etc.
default_template_path = pkg_resources.resource_filename(
    __name__,
    'data/template.html.j2')

# This is used for formatting individual chunks of code/documentation.
chunk_template_path = pkg_resources.resource_filename(
    __name__,
    'data/chunk.html.j2')


def parse_args():
    p = argparse.ArgumentParser()

    # `--template TEMPLATE`
    #
    # Path to a Jinja2 template that will be used to create the final
    # document.  See `shdoc/data/template.html.h2` for an example
    # template.
    p.add_argument('--template', '-t',
                   default=default_template_path,
                   help='Path to the HTML template')

    # `--chunk-template TEMPLATE`
    #
    # Path to a Jinja2 template that will be used to render each chunk
    # of code + documentation.  Ideally you won't need to use this one
    # much.
    p.add_argument('--chunk-template',
                   default=chunk_template_path,
                   help='Path to HTML template for code/doc chunks')

    # `--title TITLE`
    #
    # Set an explicit title for the document, rather then deriving one
    # from the input pathname.
    p.add_argument('--title', '-T',
                   help='Document title (available to template as "title")')

    # `--shortname`
    #
    # This is a boolean option that, when set, causes shdoc to use
    # just the basename of a file as the derived title, rather than
    # the full pathname.
    p.add_argument('--shortname', '-S',
                   action='store_true',
                   help='Use basename rather than full path for title')

    # `--output OUTPUT`
    #
    # Send output to a file, rather than to *stdout*.
    p.add_argument('--output', '-o')

    # `--language LANGUAGE`
    #
    # Set the value of the `language` variable passed to the template
    # if no value can be derived via an extension mapping.  Note that
    # this value has no effect unless your template uses it
    # explicitly.
    p.add_argument('--language', '-l',
                   help='Value for "language" key if no '
                   'extension mapping is available')

    # `--map-extension EXTENSION=LANGUAGE`
    #
    # Allow shdoc to derive a value for the `language` variable by
    # matching the file against a list of extensions.  You may specify
    # this option multiple times, for example:
    #
    #     shdoc -m .py=python -m .sh=shell -m .yml=yaml
    p.add_argument('--map-extension', '-m',
                   action='append',
                   default=[],
                   type=lambda x: x.split('=', 1),
                   help='Map file extensions to values for '
                   'the "language" key')

    # `--metadata KEY=VALUE`
    #
    # Provide arbitary key=value metadata that will be made available
    # to the template in the `metadata` dictionary.  For example, if
    # you run:
    #
    #     shdoc -m author='Lars Kellogg-Stedman'
    #
    # Then in your template you can reference:
    #
    #     Author: {{ metadata.author }}
    p.add_argument('--metadata', '-d',
                   action='append',
                   default=[],
                   type=lambda x: x.split('=', 1),
                   help='arbitrary key=value metadata that will be passed '
                        'to the template')

    p.add_argument('input', nargs='?')

    return p.parse_args()


# Takes a `(code, doc)` chunk from the parser and emits the
# appropriate HTML structure.  Note that for a side-by-side display
# this will require the support of CSS in your template.
def emit_chunk(code, doc, template):
    code = ''.join(escape(x) for x in code)
    doc = markdown.markdown(''.join(doc))

    return template.render(
        code=code, doc=doc)


def main():
    args = parse_args()
    args.map_extension = dict(args.map_extension)
    args.metadata = dict(args.metadata)

    with open(args.template) as fd:
        template = jinja2.Template(fd.read())

    with open(args.chunk_template) as fd:
        chunk_template = jinja2.Template(fd.read())

    content = ''
    with file_or_stdio(args.input, 'r') as infd:
        # Try to match the file extension against the extension map
        # and set the "language" key.  The "language" key is available
        # to your template and can be used, for example, to explicitly
        # enable syntax highlighting if you are using something like
        # [highlight.js][] or [prism][].
        #
        # [highlight.js]: https://highlightjs.org/
        # [prism]: http://prismjs.com/
        for ext, lname in args.map_extension.items():
            if infd.name.endswith(ext):
                args.language = lname
                break

        for code, doc in HashCommentParser(infd):
            content += emit_chunk(code, doc, chunk_template)

        # Set the title to the value of the `--title` option, if
        # provided, otherwise the base filename if `--shortname` was
        # provided, or the full path otherwise.
        title = (args.title if args.title else (
            os.path.basename(infd.name) if args.shortname
            else infd.name))

        # Render the template
        with file_or_stdio(args.output, 'w') as outfd:
            outfd.write(template.render(content=content,
                                        filename=infd.name,
                                        title=title,
                                        language=args.language,
                                        metadata=args.metadata))

if __name__ == '__main__':
    main()
