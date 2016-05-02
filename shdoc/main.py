import argparse
import jinja2
import markdown
import os
from cgi import escape

from shdoc.parser import HashCommentParser
from shdoc.util import file_or_stdio


def parse_args():
    p = argparse.ArgumentParser()

    # `--template-directory DIRECTORY`
    #
    # Path to a directory containing the jinja2 templates used to
    # render the document.  The main template is called `template.html`.
    # Any `{% include ... %}` references not found in this directory
    # will be searched for in the package `data` directory.
    p.add_argument('--template-directory', '-t',
                   help='Path to template directory')

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

    # We use a [ChoiceLoader][] so that we can find templates in a
    # user-defined directory and fall back to the package internal
    # directory.
    #
    # [choiceloader]: http://jinja.pocoo.org/docs/dev/api/#jinja2.ChoiceLoader
    loaders = [jinja2.PackageLoader(__name__, 'data')]
    if args.template_directory:
        loaders = ([jinja2.FileSystemLoader(args.template_directory)] +
                   loaders)

    env = jinja2.Environment(
        loader=jinja2.ChoiceLoader(loaders))
    doc_template = env.get_template('template.html')
    chunk_template = env.get_template('chunk.html')

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
            outfd.write(doc_template.render(
                content=content,
                filename=infd.name,
                title=title,
                language=args.language,
                metadata=args.metadata))

if __name__ == '__main__':
    main()
