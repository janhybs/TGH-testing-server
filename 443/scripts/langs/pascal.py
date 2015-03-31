__author__ = 'jan-hybs'
from process import Command, CommandResult
import os

def compile (main_file, cfg):
    root = os.path.dirname (main_file)
    output = os.path.join (root, 'error', 'compile.out')
    errput = os.path.join (root, 'error', 'compile.out')
    cmd = Command (['cd ' + root + '; fpc ' + main_file], inn=None, out=output, err=errput, shell=True)

    return cmd.run ()

def run (comp_res, main_file, inn, out, err):
    (root, ext) = os.path.splitext (main_file)
    cmd = Command ([root], inn, out, err)

    return cmd.run ()