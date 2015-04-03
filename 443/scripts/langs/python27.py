__author__ = 'jan-hybs'
from process import Command, CommandResult

def compile (main_file, cfg):
    return CommandResult()

def run (comp_res, main_file, inn, out, err):
    commands = [
        "python '{:s}'".format (main_file)
    ]
    cmd = Command (commands, inn, out, err)

    return cmd.run ()