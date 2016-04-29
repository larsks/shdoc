class Documenter(object):
    def __init__(self, fd):
        self.fd = fd

    def __iter__(self):
        return self.iter_chunks()

    def iter_chunks(self):
        indoc = False

        doc = []
        code = []
        indoc = False

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

if __name__ == '__main__':
    import sys
    with open(sys.argv[1]) as fd:
        d = Documenter(fd)
        for chunk in d:
            print "---"
            print chunk
            print
