import contextlib
import sys


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
