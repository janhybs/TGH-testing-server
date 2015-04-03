__author__ = 'jan-hybs'
from process import Command, CommandResult
import os


def compile (main_file, cfg):
    root = os.path.dirname (main_file)
    output = os.path.join (root, 'error', 'compile.out')
    errput = os.path.join (root, 'error', 'compile.out')
    commands = [
        "cd '{:s}'".format (root),
        "javac '{:s}'".format (main_file)
    ]
    cmd = Command (commands, inn=None, out=output, err=errput)

    return cmd.run ()

def run (comp_res, main_file, inn, out, err):
    (root, ext) = os.path.splitext (main_file)
    basedir = os.path.dirname (root)
    commands = [
        "java -classpath '{:s}' main".format (basedir)
    ]
    cmd = Command (commands, inn, out, err)

    return cmd.run ()
