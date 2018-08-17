import os
import os.path
import sys
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

from .escape import escape_source
from .compare import compare_output


def has_to_recompile(source, target):
    if not os.path.exists(target):
        return True
    elif os.stat(source).st_mtime >= os.stat(target).st_mtime:
        return True
    return False


def get_run_argv(filename):
    return [filename]


def default_testcase_prefix(oj, problem):
    return os.path.join(oj, problem)


def load_config_file(rootdir, filename, fallback):
    cfg = ModuleType("ixcfg")
    cfg.ROOTDIR = rootdir

    cfg.has_to_recompile = has_to_recompile
    cfg.get_run_argv = get_run_argv
    cfg.default_testcase_prefix = default_testcase_prefix

    def get_generated_files(filename):
        argv = cfg.get_compile_argv(filename)
        if argv is None:
            return []
        _, target = argv
        return [target]

    cfg.get_generated_files = get_generated_files

    d = cfg.__dict__
    if filename is not None or os.path.exists(fallback):
        if filename is None:
            filename = fallback

        with open(filename, 'r') as f:
            exec(f.read(), d)

    return cfg


def init_config(cfg):
    d = cfg.__dict__
    d.setdefault("SOLUTIONS_DIR", os.path.join(cfg.ROOTDIR, "solutions"))
    d.setdefault("TESTCASES_DIR", os.path.join(cfg.ROOTDIR, "testcases"))

    d.setdefault("VERBOSE", os.environ.get("VERBOSE", "0").lower() in ("true", "on", "1"))
    d.setdefault("NO_ASK", os.environ.get("NOASK", "0").lower() in ("true", "on", "1"))
    d.setdefault("LOGIN_MAX_RETRY", 2)

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


def compile_file(ROOTDIR, argv, source, target=None):
    logger.info("[COMPILE] %s", relative_path(ROOTDIR, source))

    logger.debug(quote_argv(argv))

    proc = Popen(argv,stdout=PIPE)
    result = proc.communicate()

    if proc.returncode == 0:
        if target:
            return target
        else:
            return result[0]

    logger.error("[ERROR] %s: compilation failed", relative_path(ROOTDIR, source))


def run_file(cfg, filename):
    argv = cfg.get_run_argv(relative_path(cfg.ROOTDIR, filename))
    logger.debug(quote_argv(argv))
    p = Popen(argv)
    if p.wait() == 0:
        return True


def run_test(cfg, filename, input, output):
    logger.info("[RUN] %s", relative_path(cfg.ROOTDIR,input))

    argv = cfg.get_run_argv(relative_path(cfg.ROOTDIR, filename))

    logger.debug(
        "cat %s | %s | compare - %s",
        quote_argv([relative_path(cfg.ROOTDIR, input)]),
        quote_argv(argv),
        quote_argv([relative_path(cfg.ROOTDIR, output)]))

    with open(input,'rb') as f:
        p = Popen(argv,stdin=f,stdout=PIPE)

    (got,_) = p.communicate()

    if p.returncode != 0:
        logger.error("[ERR] %s: Exit code = %d", relative_path(cfg.ROOTDIR,filename), p.returncode)
        return

    with open(output, 'rb') as f:
        expected = f.read()

    if compare_output(got, expected):
        return True

    logger.error("[ERR] %s: incorrect output", relative_path(cfg.ROOTDIR,filename))


def get_solution_info(cfg, filename):
    m = re.match(cfg.SOLUTION_PATTERN, relative_path(cfg.ROOTDIR, filename))
    if m is None:
        return None
    return m.group('oj'), m.group('problem')


def compile_solution(cfg, filename, recompile):
    argv = cfg.get_compile_argv(filename)
    if argv is None:
        return filename

    argv, target = argv
    if not (recompile or cfg.has_to_recompile(filename, target)):
        return target

    return compile_file(cfg.ROOTDIR, argv, filename, target)


def find_solutions(cfg, filename=None):
    if filename is None:
        filename = cfg.SOLUTIONS_DIR
    if os.path.isdir(filename):
        for root,dirs,files in os.walk(filename):
            for name in files:
                fullname = os.path.join(root,name)
                info = get_solution_info(cfg, fullname)
                if info:
                    yield fullname, info
    else:
        info = get_solution_info(cfg, filename)
        if info:
            yield filename, info


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
    data = data.replace('\r\n','\n').lstrip("\n")

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
                save_testcase(prefix+"."+k+"."+str(i+1), v)


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

    if result is False:
        return None

    save_testcases(prefix, result)

    testcases = list(_find_testcases(dirname,basename))
    if testcases:
        return testcases

    logger.error("[ERR] %s %s: no testcase found", oj, problem)


def _generate_submission(cfg, oj, problem, filename):
    client = cfg.client_loader.load(oj)
    envs = client.get_envs()
    submission = cfg.prepare_submission(list(envs.keys()), filename)

    if submission is None:
        return None

    env, code = submission
    if type(code) == bytes and env.lang == 'C':
        code = escape_source(code, chkstk=env.os=="Windows").decode("utf-8")

    return client, envs[env], code


def generate_submission(cfg, filename):
    info = get_solution_info(cfg, filename)
    if info is None:
        return None

    oj, problem = info
    submission = _generate_submission(cfg, oj, problem, filename)
    if submission is None:
        return None
    _, _, code = submission

    return code


def submit_solution(cfg, oj, problem, filename, wait=False):
    logger.info("[SUBMIT] %s", relative_path(cfg.ROOTDIR, filename))

    submission = _generate_submission(cfg, oj, problem, filename)
    if submission is None:
        return None
    client, env, code = submission

    token = client.submit(problem, env, code)

    if not token:
        logger.error("[ERR] %s: submission failed", relative_path(cfg.ROOTDIR, filename))
        return None

    if not wait:
        return True

    while True:
        sleep(2)
        try:
            result = client.check(problem, token)
        except TimeoutError:
            continue

        if not result:
            logger.error("[ERR] %s: failed to fetch result", relative_path(cfg.ROOTDIR, filename))
            return None

        if not result[0]:
            logger.info("[SUBMIT] %s: \x1b[33m%s\x1b[39m", relative_path(cfg.ROOTDIR, filename), result[1])
            continue

        if result[0]:
            if not result[2]:
                logger.info("[SUBMIT] %s: \x1b[31m%s\x1b[39m", relative_path(cfg.ROOTDIR, filename), result[1])
                return None
            else:
                if len(result) > 3 and result[3]:
                    logger.info("[SUBMIT] %s: \x1b[32m%s (%s)\x1b[39m", relative_path(cfg.ROOTDIR, filename), result[1], result[3])
                else:
                    logger.info("[SUBMIT] %s: \x1b[32m%s\x1b[39m", relative_path(cfg.ROOTDIR, filename), result[1])
            return True


def clean_generated_files(cfg, filename):
    files = [n for n in cfg.list_generated_files(filename) if os.path.exists(n)]
    if files:
        logger.info("[CLEAN] %s", relative_path(cfg.ROOTDIR, filename))
    for target in files:
        logger.debug("[REMOVE] %s", relative_path(cfg.ROOTDIR, target))
        os.remove(target)

    return True
