class HashCommentParser(object):
    def __init__(self, fd):
        self.fd = fd

    # This class is an iterator, which means that after you do this:
    #
    #     with open('somefile') as fd:
    #         doc = HashCommentParser(fd)
    #
    # You can then iterate over `(code, documentation)` chunks
    # like this:
    #
    #         for codepart, docpart in doc:
    #             ...
    def __iter__(self):
        return self.iter_chunks()

    def iter_chunks(self):
        indoc = False

        doc = []
        code = []
        indoc = False

        # Iterate over lines in the input file looking for
        # documentation (lines that start with `# `, preceded
        # by an arbitrary amount of whitespace).
        for line in self.fd:
            if line.strip().startswith('# ') and not indoc:
                if doc:
                    yield (code, doc)
                    code = []
                    doc = []
                doc.append(line.strip()[2:])
                indoc = True
            elif line.strip().startswith('# '):
                doc.append(line.strip()[2:])
            elif (doc and line.strip() == '#'):
                doc.append('')
            else:
                indoc = False
                code.append(line)

        yield (code, doc)

# Allow simple debugging from the command line.  When run as `__main__`,
# open the first filename passed on the command line and print out all
# chunks returned by the parser.
if __name__ == '__main__':
    import sys
    with open(sys.argv[1]) as fd:
        d = HashCommentParser(fd)
        for chunk in d:
            print "---"
            print chunk
            print
