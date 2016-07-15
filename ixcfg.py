from ix.utils import replace_ext
import os.path

SOLUTION_PATTERN = r'^(?P<oj>\w+)(?:/.*)?/(?P<problem>[A-Za-z0-9_\-]+)\.c$'

def get_compile_argv(filename):
    target = replace_ext(filename, "elf")
    return ['gcc', '-Wall','-Wextra','-Werror','-o', target, filename], target


def prepare_submission(compilers, filename):
    compilers = [c for c in compilers if c.lang == 'C' and c.name in ('MinGW', 'GCC')]
    if not compilers:
        return None
    with open(filename,'r') as f:
        code = f.read()
    return compilers[0], code
