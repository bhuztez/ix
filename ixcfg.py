import os.path

SOLUTION_PATTERN = r'^(?P<oj>\w+)(?:/.*)?/(?P<problem>\w+)\.c$'


def get_compile_argv(filename):
    target = os.path.splitext(filename)[0]+".elf"
    return ['gcc', '-Wall','-Wextra','-Werror','-o', target, filename], target


def prepare_submission(compilers, code):
    compilers = [c for c in compilers if c.lang == 'C' and c.name in ('MinGW', 'GCC')]
    if not compilers:
        return None
    return compilers[0], code
