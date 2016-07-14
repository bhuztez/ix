import os
import os.path
from .cmd import command, main
from . import load_config_file, init_config

rootdir = os.getcwd()
cmd, args = command.parse()
cfg = load_config_file(rootdir, args.config, os.path.join(rootdir, "ixcfg.py"))
init_config(cfg)
main(cmd, args, cfg)
