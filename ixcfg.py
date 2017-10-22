from ix.utils import replace_ext

SOLUTION_PATTERN = r'^(?P<oj>\w+)(?:/.*)?/(?P<problem>[A-Za-z0-9_\-]+)\.c$'

def get_compile_argv(filename):
    target = replace_ext(filename, "elf")
    return ['gcc', '-Wall','-Wextra','-Werror','-o', target, filename], target


def prepare_submission(envs, filename):
    envs = [c for c in envs if c.lang == 'C' and c.name in ('MinGW', 'GCC')]
    if not envs:
        return None
    with open(filename,'r') as f:
        code = f.read()
    return envs[0], code
