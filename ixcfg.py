import subprocess
from ix.utils import replace_ext, index_of

SOLUTION_PATTERN = r'^(?:[^/]+)/(?P<oj>\w+)(?:/.*)?/(?P<problem>[A-Za-z0-9_\-]+)\.c$'

def get_compile_argv(filename):
    target = replace_ext(filename, "elf")
    return ['gcc', '-Wall','-Wextra','-Werror','-o', target, filename], target

def get_llvm_target(env):
    return ( ({"x86": "i686", "x86_64": "x86_64"}[env.arch])
             + "-" +
             ({"Windows": "pc-windows", "Linux": "unknown-linux"}[env.os]) + "-gnu")

def pick_env(envs):
    envs = [c for c in envs if c.lang == "C" and c.name in ("GCC", "MinGW")]
    envs.sort(key=lambda c: (index_of(['Linux','Windows'], c.os), index_of(['x86_64','x86'], c.arch)))
    if envs:
        return envs[0]

def generate_submission(filename, llvm_target):
    argv = ['clang', '-target', llvm_target, '-S', '-o-', filename]
    return subprocess.check_output(argv)

def prepare_submission(envs, filename):
    env = pick_env(envs)
    if not env:
        return None

    llvm_target = get_llvm_target(env)
    code = generate_submission(filename, llvm_target)
    return env, code
