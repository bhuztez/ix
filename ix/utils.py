import os.path

def index_of(l, x):
    try:
        return l.index(x)
    except ValueError:
        return len(x)

def replace_ext(filename, ext):
    return os.path.splitext(filename)[0]+"."+ext
