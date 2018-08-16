import os
import sys
import subprocess
from ix.utils import replace_ext, index_of

SOLUTION_PATTERN = r'^(?:[^/]+)/(?P<oj>\w+)(?:/.*)?/(?P<problem>[A-Za-z0-9_\-]+)\.c$'

def get_compile_argv(filename):
    target = replace_ext(filename, "elf")
    return ['clang', '-Wall','-Wextra','-Werror','-o', target, filename], target

def list_generated_files(filename):
    return [replace_ext(filename, ext) for ext in ["elf"]]

def get_llvm_target(env):
    return ( ({"x86": "i686", "x86_64": "x86_64"}[env.arch])
             + "-" +
             ({"Windows": "pc-windows", "Linux": "unknown-linux"}[env.os]) + "-gnu")

def get_mingw_include(env):
    if env.os != "Windows":
        return []

    arch = ({"x86": "i686", "x86_64": "x86_64"}[env.arch])

    if sys.platform == 'linux':
        prefix = os.path.join('/usr', arch + '-w64-mingw32')
        return ['-isystem', os.path.join(prefix, 'include'),
                '-isystem', os.path.join(prefix, 'sys-root/mingw/include')]
    elif sys.platform == 'darwin':
        import json
        info = json.loads(subprocess.check_output(["brew", "info", "--json=v1", "mingw-w64"]))[0]
        cellar = info["bottle"]["stable"]["cellar"]
        version = info["linked_keg"]
        return ['-isystem', os.path.join(cellar, 'mingw-w64', version, 'toolchain-'+arch, arch + '-w64-mingw32', 'include')]
    else:
        return []


def pick_env(envs):
    envs = [c for c in envs if c.lang == "C" and c.name in ("GCC", "MinGW")]
    envs.sort(key=lambda c: (index_of(['Linux','Windows'], c.os), index_of(['x86_64','x86'], c.arch)))
    if envs:
        return envs[0]

def generate_submission(filename, env):
    llvm_target = get_llvm_target(env)
    INCLUDE = get_mingw_include(env)
    VERBOSE_FLAG = ['-v'] if VERBOSE else []
    argv = ['clang', '-target', llvm_target] + VERBOSE_FLAG + INCLUDE + ['-S', '-o-', filename]
    return subprocess.check_output(argv)

def prepare_submission(envs, filename):
    env = pick_env(envs)
    if not env:
        return None

    code = generate_submission(filename, env)
    return env, code
