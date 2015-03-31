__author__ = 'jan-hybs'
from process import Command, CommandResult
import os

def compile (main_file, cfg):
    root = os.path.dirname (main_file)
    output = os.path.join (root, 'error', 'compile.out')
    errput = os.path.join (root, 'error', 'compile.err')
    cmd = Command (['gmcs', main_file], inn=None, out=output, err=errput)

    return cmd.run ()

def run (comp_res, main_file, inn, out, err):
    (root, ext) = os.path.splitext (main_file)
    exe_name = root + '.exe'
    cmd = Command (['mono', exe_name], inn, out, err)

    return cmd.run ()
