#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import threading
from subprocess import Popen, PIPE
import json
import importlib
import datetime
import time



MAX_DURATION = 60
DIFF_OUTPUT = {
    '0' : 'spravny-vystup',
    '1': 'chybny-vystup',
    '2': 'zadny-vystup'
}
DIFF_OUTPUT_SHORT = {
    '0' : 'OK',
    '1': 'ER',
    '2': 'ER'
}
RESULT_LETTER = {
    '0': 'A', # accepted
    '1': 'E', # error
    '2': 'E', # compilation error
    '3': 'E', # run error
    '4': 'W'  # wrong answer
}


class Timer (object):
    # def __init__(self, name=None):
    #     self.name = name
    #     self.duration = None
    #
    # def __enter__(self):
    #     self.tstart = time.time()
    #
    # def __exit__(self, type, value, traceback):
    #     if self.name:
    #         print '[%s]' % self.name,
    #     print 'Elapsed: %s' % (time.time() - self.tstart)

    def __init__(self, name=None):
        self.time = 0
        self.name = name
        self.duration = 0

    def tick (self):
        self.time = time.time()

    def tock (self):
        self.duration =  time.time() - self.time

    def __repr__(self):
        if self.name is None:
            return "{:1.6f}".format(self.duration)
        return "{:s}: {:1.6f}".format(self.name, self.duration)





class CommandResult (object):

    def __init__ (self, exit=None, error=None, cmd=None):
        self.exit = exit
        self.error = error
        self.cmd = cmd

    def isempty (self):
        return self.exit is None

    def isok (self):
        return self.exit == 0

    def isnotwrong (self):
        return self.isok () or self.isempty ()

    def __repr__(self):
        return "[CommandResult exit:{:d} {:s} {}]".format (self.exit, self.error, self.cmd)

    @staticmethod
    def loadfile (path, mode='r'):
        if not os.path.isfile (str(path)):
            return ''

        with open (path, mode) as f:
            return f.read()




class Command (object):
    def __init__(self, args, inn=None, out=None, err=None, shell=False):
        self.args = args
        self.timer = Timer(' '.join(args))
        self.process = None
        self.fatal_error = None

        self.shell = shell
        self.inn = self.inn_path = inn
        self.out = self.out_path = out
        self.err = self.err_path = err

        self.duration = 0
        # print 'running: {} < {} > {} 2> {}'.format (' '.join (self.args), self.inn, self.out, self.err)

    def open_files (self):
        self.inn = PIPE if self.inn is None else open (self.inn, "rb")
        self.out = PIPE if self.out is None else open (self.out, "wb")
        self.err = PIPE if self.err is None else open (self.err, "wb")


    def close_files (self):
        if not self.inn is PIPE: self.inn.close ()
        if not self.out is PIPE: self.out.close ()
        if not self.err is PIPE: self.err.close ()

    def __repr__(self):
        return "[Command: {}".format (' '.join (self.args))

    def run(self, timeout=MAX_DURATION):

        self.open_files ()

        def target():
            try:
                self.process = Popen (self.args, stdout=self.out, stderr=self.err, stdin=self.inn, shell=self.shell)
                self.process.communicate ()
            except Exception as e:
                # if shell is False exception can be thrown
                print 'Fatal error'
                print e
                self.fatal_error = str(e) + "\n"
                self.fatal_error += str(self) + "\n"
                if hasattr(e, 'child_traceback'):
                    self.fatal_error += str(e.child_traceback)

        # create thread
        thread = threading.Thread (target=target)

        # run thread
        self.timer.tick ()
        thread.start ()
        thread.join (timeout)
        self.timer.tock ()

        # kill longer processes
        if thread.is_alive ():
            self.process.terminate ()
            thread.join ()


        # files
        self.close_files ()

        # on error return error
        if self.fatal_error is not None:
            return CommandResult (1, str(self.fatal_error), self)


        # return process if no FATAL error occurred
        err_msg = (CommandResult.loadfile(self.err_path) + CommandResult.loadfile(self.out_path)).lstrip()
        return CommandResult (self.process.returncode, err_msg, self)

def get_module (cls):
    return importlib.import_module ("langs." + cls)

def change_ext (filename, new_ext):
    (root, ext) = os.path.splitext(os.path.basename(filename))
    return root + new_ext

def mkdirs (path, mode):
    oldmask = os.umask (0)
    os.makedirs (path, mode)
    os.umask (oldmask)

def compare (a, b):
    result = None
    with open (a, 'rb') as f1, open (b, 'rb') as f2:
        while True:
            l1 = f1.readline()
            l2 = f2.readline()

            while l1.isspace():
                l1 = f1.readline()

            while l2.isspace():
                l2 = f2.readline()

            if l1 == '' and l2 == '':
                result = 0
                break

            if l1 != l2 or l1 == '' or l2 == '':
                result = 1
                break
    return result

def enc (v):
    return v.encode ('utf-8')



def main (config_path):
    # load config
    try:
        with open(config_path, 'r') as config:
            cfg = json.load (config, encoding="utf-8")
    except Exception as e:
        print e


    # print cfg['lang']['id']
    # print cfg
    # print '------------------------------------'

    # dynamically get module
    lang            = cfg['lang']['id']
    problem         = cfg['problem']['id']

    problem_root    = cfg['problem']['root']
    result_root     = cfg['root']
    main_file       = os.path.join(result_root, cfg['filename'])

    try:
        mod = get_module(lang)
    except Exception as e:
        print e


    # get dirs
    inn_dir     = os.path.join(problem_root, 'input')
    ref_out_dir = os.path.join(problem_root, 'output')
    res_out_dir = os.path.join(result_root, 'output')
    res_err_dir = os.path.join(result_root, 'error')

    # get files
    inn_files     = cfg['problem']['input'] if cfg['problem'].has_key ('input') else os.listdir (inn_dir)
    ref_out_files = [os.path.join (ref_out_dir, change_ext (inn, '.out')) for inn in inn_files]
    res_out_files = [os.path.join (res_out_dir, change_ext (inn, '.out')) for inn in inn_files]
    res_err_files = [os.path.join (res_err_dir, change_ext (inn, '.err')) for inn in inn_files]
    inn_files     = [os.path.join (inn_dir, inn) for inn in inn_files]

    if not os.path.exists(res_out_dir):
        mkdirs (res_out_dir, 0o775)

    if not os.path.exists(res_err_dir):
        mkdirs (res_err_dir, 0o775)

    # compilation
    """@type CommandResult"""
    comp_res = mod.compile (main_file, cfg)

    exec_res = []
    diff_res = []
    result = ""
    result += "{:12s} {} ({})\n".format ('uloha', enc (cfg['problem']['name']), problem)
    result += "{:12s} {}\n".format ('jazyk',    lang)
    result += "{:12s} {}\n".format ('student',  cfg['user']['username'])
    result += "{:12s} {}\n".format ('datum',    datetime.datetime.now ())
    result += "{:12s} {}.\n".format ('pokus',    cfg['attempt'])

    result += '\n'

    errors = []
    outputs = []

    if comp_res.isnotwrong ():

        # execution on all input files
        for i in range(len(inn_files)):
            # run


            cur_exec_res = mod.run (comp_res, main_file, inn_files[i], res_out_files[i], res_err_files[i])


            # append details
            exec_res.append (cur_exec_res.exit)
            errors.append (CommandResult.loadfile(res_err_files[i]))



            # compare outputs
            if cur_exec_res.isok ():
                cur_diff_res = compare (res_out_files[i], ref_out_files[i])
            else:
                cur_diff_res = 2
            outputs.append({'path': os.path.basename(res_out_files[i]), 'exit': max([cur_exec_res.exit, cur_diff_res])})
            diff_res.append (cur_diff_res)


            result += "[{:2s}] {:2d}. sada: {:20s} {:6.3f} ms {:s} \n".format (
                DIFF_OUTPUT_SHORT[str(cur_diff_res)], i+1,
                os.path.basename(res_out_files[i]),
                cur_exec_res.cmd.timer.duration * 1000,
                DIFF_OUTPUT[str(cur_diff_res)]
            )


    if comp_res.isnotwrong () and max(exec_res) == 0 and max(diff_res) == 0:
        result += "\nodevzdane reseni je spravne\n"
        res_code = 0
    else:
        result += "\nodevzdane reseni je chybne:\n"
        res_code = 1
        if not comp_res.isnotwrong ():
            result += "\tchyba pri kompilaci({}):\n{}\n".format (comp_res.exit, comp_res.error)
            res_code = 2

        if len (exec_res) and max (exec_res) != 0:
            result += "\tchyba pri behu programu: kod ukonceni {:d}\n\t".format (max (exec_res))
            result += "\n\t".join (errors)
            res_code = 3

        if len (diff_res) and max (diff_res) != 0:
            result += "\tchybny vystup"
            res_code = 4

    # specify new result_root based on result exit
    new_result_root = "{:s}_{:s}".format (result_root, RESULT_LETTER[str(res_code)])

    with open (os.path.join(result_root, 'result.txt'), 'w') as f:
        f.write (result)

    print result

    # fix paths to reflect end result
    outputs = [{'path': os.path.join (new_result_root, 'output', output['path']), 'exit': output['exit']} for output in outputs]
    php_info = {'exit': res_code, "outputs": outputs }
    json.dump (php_info, sys.stdout)


    # try to rename folder
    os.rename(result_root, new_result_root)

if __name__ == '__main__':
    try:
        main (sys.argv[1])
        sys.exit(0)
    except Exception as e:
        print e
        sys.exit(1)
