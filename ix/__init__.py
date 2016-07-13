import os
import os.path
import re
from subprocess import Popen, PIPE
from types import ModuleType
from time import sleep
import logging
logger = logging.getLogger(__name__)

import platform
if platform.system() == 'Windows':
    from subprocess import list2cmdline as quote_argv
else:
    from pipes import quote
    def quote_argv(argv):
        return " ".join(quote(a) for a in argv)


def has_to_recompile(source, target):
    if not os.path.exists(target):
        return True
    elif os.stat(source).st_mtime >= os.stat(target).st_mtime:
        return True
    return False


def get_solution_info(filename):
    m = re.match(r'^(\w+)(?:/.*)?/(\w+)\.\w+$', filename)
    if m:
        return (m.group(1), m.group(2))


def get_run_argv(filename):
    return [filename]


def default_testcase_prefix(oj, problem):
    return os.path.join(oj, problem)


def load_config_file(rootdir, filename, no_skip):
    cfg = ModuleType("ixcfg")
    cfg.ROOTDIR = rootdir

    d = cfg.__dict__

    if os.path.exists(filename) or no_skip:
        with open(filename, 'r') as f:
            exec(f.read(), d)

    d.setdefault("VERBOSE", os.environ.get("VERBOSE", "0").lower() in ("true", "on", "1"))
    d.setdefault("NO_ASK", os.environ.get("NOASK", "0").lower() in ("true", "on", "1"))
    d.setdefault("SOLUTIONS_DIR", os.path.join(cfg.ROOTDIR, "solutions"))
    d.setdefault("TESTCASES_DIR", os.path.join(cfg.ROOTDIR, "testcases"))
    d.setdefault("LOGIN_MAX_RETRY", 2)
    d.setdefault("has_to_recompile", has_to_recompile)
    d.setdefault("get_solution_info", get_solution_info)
    d.setdefault("get_run_argv", get_run_argv)
    d.setdefault("default_testcase_prefix", default_testcase_prefix)

    if platform.system() not in ('Windows','Java'):
        if not hasattr(cfg, "CREDENTIAL_READER"):
            from ix.credential.readers.readline import ReadlineCredentialReader
            cfg.CREDENTIAL_READER = ReadlineCredentialReader()

    if not hasattr(cfg, "CREDENTIAL_STORAGE"):
        from ix.credential.storages.sqlite import SqliteCredentialStorage
        cfg.CREDENTIAL_STORAGE = SqliteCredentialStorage(os.path.join(cfg.ROOTDIR, "credentials.sqlite"))

    return cfg


def relative_path(basedir, filename):
    basedir = os.path.abspath(basedir)
    filename = os.path.abspath(filename)

    if os.path.commonprefix([filename,basedir]) == basedir:
        return os.path.relpath(filename, basedir)
    else:
        return filename


def compile_file(cfg, argv, source, target=None):
    logger.info("[COMPILE] %s", relative_path(cfg.ROOTDIR, source))

    logger.debug(quote_argv(argv))

    proc = Popen(argv,stdout=PIPE)
    result = proc.communicate()

    if proc.returncode == 0:
        if target:
            return target
        else:
            return result[0]

    logger.error("[ERROR] %s: compilation failed", relative_path(cfg.ROOTDIR, source))


def run_file(cfg, filename):
    argv = cfg.get_run_argv(os.path.relpath(filename))
    logger.debug(quote_argv(argv))
    p = Popen(argv)
    if p.wait() == 0:
        return True


def run_test(cfg, filename, input, output):
    from difflib import unified_diff
    from io import StringIO
    logger.info("[RUN] %s", relative_path(cfg.ROOTDIR,input))

    logger.debug("%s < %s | diff - %s" %(
        quote_argv([relative_path(cfg.ROOTDIR, filename)]),
        quote_argv([relative_path(cfg.ROOTDIR, input)]),
        quote_argv([relative_path(cfg.ROOTDIR, output)])))

    with open(input,'rb') as f:
        p = Popen([filename],stdin=f,stdout=PIPE)

    (got,_)= p.communicate()

    if p.returncode != 0:
        logger.error("[ERR] %s: Exit code = %d", relative_path(cfg.ROOTDIR,filename), p.returncode)
        return

    got_lines = StringIO(got.decode('utf-8')).readlines()
    with open(output,'r') as f:
        expected_lines = f.readlines()

    diffs=list(unified_diff(got_lines,expected_lines,"/dev/stdout",output))
    if not diffs:
        return True
    sys.stdout.writelines(diffs)

    logger.error("[ERR] %s: incorrect output", relative_path(cfg.ROOTDIR,filename))


def compile_solution(cfg, filename, recompile):
    info = cfg.get_solution_info(relative_path(cfg.SOLUTIONS_DIR, filename))
    if info is None:
        return None

    argv = cfg.get_compile_argv(filename)
    if argv is None:
        return filename

    argv, target = argv
    if not (recompile or cfg.has_to_recompile(filename, target)):
        return target

    return compile_file(cfg, argv, filename, target)


def find_solutions(cfg, filename=None):
    if filename is None:
        filename = cfg.SOLUTIONS_DIR
    if os.path.isdir(filename):
        for root,dirs,files in os.walk(filename):
            for name in files:
                fullname = os.path.join(root,name)
                info = cfg.get_solution_info(relative_path(cfg.SOLUTIONS_DIR, fullname))
                if info:
                    yield os.path.abspath(fullname), info
    else:
        info = cfg.get_solution_info(relative_path(cfg.SOLUTIONS_DIR, filename))
        if info:
            yield os.path.abspath(filename), info


def _find_testcases(dirname, basename):
    inprefix = basename + ".in"

    for inname in os.listdir(dirname):
        if not inname.startswith(inprefix):
            continue
        outname = os.path.join(dirname, basename +".out" + inname[len(inprefix):])
        if not os.path.exists(outname):
            continue
        yield os.path.join(dirname,inname), outname


def save_testcase(filename, data):
    if not data.endswith("\n"):
        data += "\n"

    with open(filename,"w") as f:
        f.write(data)


def save_testcases(prefix, testcases):
    if len(testcases) == 1:
        for k, v in testcases[0].items():
            save_testcase(prefix+"."+k, v)
    else:
        for i, testcase in enumerate(testcases):
            for k, v in testcase.items():
                save_testcase(prefix+"."+k+"."+str(i), v)


def find_testcases(cfg, oj, problem):
    prefix = os.path.join(
        cfg.TESTCASES_DIR,
        getattr(cfg, "testcase_prefixes", {}).get(oj, lambda problem: cfg.default_testcase_prefix(oj, problem))(problem))

    basename = os.path.basename(prefix)
    dirname = os.path.dirname(prefix)
    os.makedirs(dirname, exist_ok=True)

    testcases = list(_find_testcases(dirname,basename))
    if testcases:
        return testcases

    client = cfg.client_loader.load(oj)
    result = client.fetch(problem)

    if not result:
        return None

    save_testcases(prefix, result)

    testcases = list(_find_testcases(dirname,basename))
    if testcases:
        return testcases

    logger.error("[ERR] %s %s: no testcase found", oj, problem)


def generate_submission(cfg, filename):
    info = cfg.get_solution_info(relative_path(cfg.SOLUTIONS_DIR, filename))
    if info is None:
        return None

    oj, problem = info
    client = cfg.client_loader.load(oj)
    compilers = client.get_compilers()

    with open(filename, 'r') as f:
        code = f.read()
    submission = cfg.prepare_submission(list(compilers.keys()), code)

    if submission is None:
        return None

    compiler, code = submission
    return code


def submit_solution(cfg, oj, problem, filename, wait=False):
    logger.info("[SUBMIT] %s", relative_path(cfg.ROOTDIR, filename))

    client = cfg.client_loader.load(oj)
    compilers = client.get_compilers()

    with open(filename, 'r') as f:
        code = f.read()
    submission = cfg.prepare_submission(list(compilers.keys()), code)

    if submission is None:
        return None

    compiler, code = submission
    token = client.submit(problem, compilers[compiler], code)

    if token is None:
        logger.error("[ERR] %s: submission failed", relative_path(cfg.ROOTDIR, filename))
        return None

    if not wait:
        return True

    while True:
        sleep(2)
        result = client.check(problem, token)
        if not result:
            logger.error("[ERR] %s: failed to fetch result", relative_path(cfg.ROOTDIR, filename))
            break

        if result[0]:
            if not result[2]:
                logger.info("[SUBMIT] %s: \x1b[31m%s\x1b[39m", relative_path(cfg.ROOTDIR, filename), result[1])
            else:
                if len(result) > 3 and result[3]:
                    logger.info("[SUBMIT] %s: \x1b[32m%s (%s)\x1b[39m", relative_path(cfg.ROOTDIR, filename), result[1], result[3])
                else:
                    logger.info("[SUBMIT] %s: \x1b[32m%s\x1b[39m", relative_path(cfg.ROOTDIR, filename), result[1])
            break

        if not result[0]:
            logger.info("[SUBMIT] %s: \x1b[33m%s\x1b[39m", relative_path(cfg.ROOTDIR, filename), result[1])

    return True
