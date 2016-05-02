This is a tool for generating HTML documentation from anything that
uses `#` as a comment character.  I originally put it together for
producing documentation from [Ansible][] playbooks, but it works
equally well with Python, shell scripts, etc.

[ansible]: http://ansible.com/

## Synopsis

    usage: shdoc [-h] [--template TEMPLATE] [--chunk-template CHUNK_TEMPLATE]
                 [--title TITLE] [--shortname] [--output OUTPUT]
                 [--language LANGUAGE] [--map-extension MAP_EXTENSION]
                 [--metadata METADATA]
                 [input]


## Options

- `--template-directory`, `-t` `DIRECTORY`

  Specifies the path to a directory containing [Jinja2][] templates.  The
  main template is called `template.html`.  You may override any or
  all of the internal templates.

- `--title`, `-T` `TITLE`

  Set the document title.  This will be available to the template as
  the `title` variable.

- `--shortname`

  By default, if you don't provide an explicit title with `--title`,
  the document title will be the full path of the input document.  If
  you specify `--shortname`, the title will be the basename of the
  input document.

- `--output`, `-o` `OUTPUT`

  Send output to the named file, rather than `stdout`.

- `--language`, `-l` `LANGUAGE`

  Set the default value of the `language` variable to `LANGUAGE`.
  This value will be used if a language cannot be determined from an
  extension mapping (see `--map-extension`).  This value will be
  available to your template in the `language` variable.

- `--map-extension`, `-m` `EXT=LANGUAGE`

  Map file extensions to values of the `language` keyword.  For
  example, `-m .py=python` would set `language` to `python` if you are
  processing a `.py` file.

  This option may be specified multiple times:

      shdoc -m .py=python -m .yml=yaml ...

- `--metadata`, `-d` `KEY=VALUE`

  Sets arbitrary metadata that will be available to your templates in
  the `metadata` dictionary.

[jinja2]: http://jinja.pocoo.org/docs/dev/templates/

## Example

Run:

    shdoc shdoc/main.py --title 'An Example' -o main.html

And then open the resulting `main.html` file in your browser.  This
will render `shdoc/main.py` using the default template, which isn't
very pretty but shows how things work.

For real world use, you would probably want a fancier template,
possibly including things like Javascript-driven syntax highlighting.

## License

shdoc, a documentation generator  
Copyright (C) 2016 Lars Kellogg-Stedman <lars@oddbit.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
