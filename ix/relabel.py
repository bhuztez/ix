import re

GLOBL = re.compile(rb'^\s+[.]globl\s+(\S+)$', re.M)
LABEL = re.compile(rb'^([^:\s]+):$', re.M)
COMMENT= re.compile(rb'\s+\#.*$', re.M)
CHARS = b'_.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

def encode_int(n):
    while True:
        yield CHARS[n % 64]
        if n == 0:
            break
        n //= 64

def relabel(code):
    code = COMMENT.sub(b'', code)
    labels = set(LABEL.findall(code)) - set(GLOBL.findall(code))
    pattern = b"|".join(map(re.escape, labels))
    labels = {l: b"L"+bytes(encode_int(n))
              for n,l in enumerate(labels)}
    def repl(m):
        return labels[m.group(0)]
    return re.sub(pattern, repl, code)
