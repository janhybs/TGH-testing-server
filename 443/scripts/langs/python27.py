__author__ = 'jan-hybs'
from process import Command, CommandResult

def compile (main_file, cfg):
    return CommandResult()

def run (comp_res, main_file, inn, out, err):
    cmd = Command (['python', main_file], inn, out, err)

    return cmd.run ()