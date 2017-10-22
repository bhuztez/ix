import os
import os.path
from argparse import ArgumentParser
from functools import wraps

import logging
logging.captureWarnings(True)
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter(fmt='%(message)s',datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

from . import (
    compile_solution, run_file, run_test,
    find_solutions, find_testcases,
    generate_submission, submit_solution
)

from .clients import ClientLoader


def argument(*args, **kwargs):
    return lambda parser: parser.add_argument(*args, **kwargs)


class Command(object):

    def __init__(self, parser):
        self._parser = parser
        self._subparsers = parser.add_subparsers(dest="COMMAND")
        self._commands = {}

    def __call__(self, *arguments):
        def decorator(func):
            name = func.__name__.replace("_", "-")
            subparser = self._subparsers.add_parser(name, help = func.__doc__)
            dests = [arg(subparser).dest for arg in arguments]

            @wraps(func)
            def wrapper(cfg,args):
                return func(cfg,**{d:getattr(args, d) for d in dests if getattr(args, d) is not None})

            self._commands[name] = wrapper
            return wrapper
        return decorator

    def parse(self):
        args = self._parser.parse_args()
        return self._commands[args.COMMAND or "help"], args


parser = ArgumentParser(description="IX")
parser.add_argument("-k","--keep-going",action="store_true",default=False,help="keep going when some task failed")
parser.add_argument("-v","--verbose",action="store_true",default=False,help="show verbose outputs")
parser.add_argument("--no-ask",action="store_true",default=False,help="do not ask for password")
parser.add_argument("-c","--config",metavar="CFG",help="use config file at CFG")
command = Command(parser)


@command(
    argument("-r", "--recompile", action="store_true", help="recompile if already compiled before run"),
    argument("filename", help="path to solution"))
def run(cfg, filename, recompile=False):
    """run solution"""
    target = yield compile_solution(cfg, filename, recompile)
    if target is None:
        return
    yield run_file(cfg, target)


@command(
    argument("-r", "--recompile", action="store_true", help="recompile if already compiled before test"),
    argument("filename", nargs='?', help="path to solution"))
def test(cfg, filename=None, recompile=False):
    """check solution against sample testcases"""
    for filename, (oj, problem) in find_solutions(cfg, filename):
        target = yield compile_solution(cfg, filename, recompile)

        if target is None:
            continue

        testcases = yield find_testcases(cfg, oj, problem)
        if testcases is None:
            continue

        for input, output in testcases:
            yield run_test(cfg, target, input, output)

@command(
    argument("filename", nargs='?', help="path to solution"))
def generate(cfg, filename=None, wait=False):
    """print the code to be submitted"""
    code = yield generate_submission(cfg, filename)
    print(code)


@command(
    argument("-w","--wait",action="store_true",default=False, help="wait until verdict"),
    argument("filename", nargs='?', help="path to solution"))
def submit(cfg, filename=None, wait=False):
    """submit solution"""
    for filename, (oj, problem) in find_solutions(cfg, filename):
        yield submit_solution(cfg, oj, problem, filename, wait)


@command(
    argument("filename", nargs='?', help="path to solution"))
def clean(cfg, filename=None, wait=False):
    """removes generated files"""
    for filename, (oj, problem) in find_solutions(cfg, filename):
        argv = cfg.get_compile_argv(filename)
        if argv is None:
            continue
        argv, target = argv
        if os.path.exists(target):
            os.remove(target)


@command()
def help(cfg):
    """Print help message"""
    parser.print_help()



def main(cmd, args, cfg):
    if args.no_ask:
        cfg.NO_ASK = True
    if args.verbose:
        cfg.VERBOSE = True

    handler.setLevel(logging.DEBUG if cfg.VERBOSE else logging.INFO)

    keep_going = args.keep_going
    error_occured = False

    cfg.client_loader = ClientLoader(cfg)

    g = cmd(cfg,args)
    if g is None:
        return

    result = None

    while True:
        try:
            result = g.send(result)
        except StopIteration:
            break

        if result is None:
            error_occured = True

            if not keep_going:
                break

    if error_occured:
        exit(1)

    exit(0)
