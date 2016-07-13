import os.path

def get_compile_argv(filename):
    if not filename.endswith(".c"):
        return
    target = os.path.splitext(filename)[0]+".elf"
    return ['gcc', '-Wall','-Wextra','-Werror','-o', target, filename], target


def prepare_submission(compilers, code):
    compilers = [c for c in compilers if c.lang == 'C' and c.name in ('MinGW', 'GCC')]
    if not compilers:
        return None
    return compilers[0], code
