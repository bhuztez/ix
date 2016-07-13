import os
from .cmd import command, main
from . import load_config_file

rootdir = os.getcwd()
cmd, args = command.parse()
config_file = os.path.join(rootdir, "ixcfg.py")
if args.config is not None:
    config_file = args.config

cfg = load_config_file(rootdir, config_file, args.config is not None)

main(cmd, args, cfg)
