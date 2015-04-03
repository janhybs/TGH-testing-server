#!/usr/bin/env python
# -*- coding: utf-8 -*-
# docker centos mod pyt

import sys
import os
import threading
from subprocess import Popen, PIPE
import json
import importlib
import datetime
import time
import getpass
from optparse import OptionParser
from daemon import Daemon



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
    def __init__(self, args, inn=None, out=None, err=None):
        # args.append ("exit") # terminate just in case
        self.command = '; ' . join (args)
        self.timer = Timer (self.command)
        self.process = None
        self.fatal_error = None

        self.shell = True
        self.inn = self.inn_path = inn
        self.out = self.out_path = out
        self.err = self.err_path = err

        self.duration = 0
        print self.command
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
        return "[Command: {}".format (self.command)

    def run(self, timeout=MAX_DURATION):

        self.open_files ()

        def target():
            try:
                self.process = Popen ([self.command], stdout=self.out, stderr=self.err, stdin=self.inn, shell=self.shell)
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
            return CommandResult (1, str (self.fatal_error), self)


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


def process (cfg):
    # print cfg['lang']['id']
    # print cfg
    # print '------------------------------------'

    # dynamically get module
    lang            = cfg['lang']['id']
    problem         = cfg['problem']['id']
    root            = cfg['root']
    result_file     = cfg['result']
    main_file       = os.path.join(root, cfg['filename'])


    try:
        mod = get_module(lang)
    except Exception as e:
        print e



    # get dirs
    inn_dir     = os.path.join(root, 'input')
    ref_out_dir = os.path.join(root, 'ref')
    res_out_dir = os.path.join(root, 'output')
    res_err_dir = os.path.join(root, 'error')

    # get files
    inn_files     = cfg['problem']['input']
    ref_out_files = [os.path.join (ref_out_dir, change_ext (inn, '.out')) for inn in inn_files]
    res_out_files = [os.path.join (res_out_dir, change_ext (inn, '.out')) for inn in inn_files]
    res_err_files = [os.path.join (res_err_dir, change_ext (inn, '.err')) for inn in inn_files]
    inn_files     = [os.path.join (inn_dir, inn) for inn in inn_files]

    # if not os.path.exists(res_out_dir):
    #     mkdirs (res_out_dir, 0o775)
    #
    # if not os.path.exists(res_err_dir):
    #     mkdirs (res_err_dir, 0o775)

    exec_res = []
    diff_res = []
    result_msg = ""
    result_msg += "{:12s} {} ({})\n".format ('uloha', enc (cfg['problem']['name']), problem)
    result_msg += "{:12s} {}\n".format ('jazyk',    lang)
    result_msg += "{:12s} {}\n".format ('student',  cfg['user']['username'])
    result_msg += "{:12s} {}\n".format ('datum',    datetime.datetime.now ())
    result_msg += "{:12s} {}.\n".format ('pokus',    cfg['attempt'])

    result_msg += '\n'

    errors = []
    outputs = []


    # compilation
    comp_res = mod.compile (main_file, cfg)

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


            result_msg += "[{:2s}] {:2d}. sada: {:20s} {:6.3f} ms {:s} \n".format (
                DIFF_OUTPUT_SHORT[str(cur_diff_res)], i+1,
                os.path.basename(res_out_files[i]),
                cur_exec_res.cmd.timer.duration * 1000,
                DIFF_OUTPUT[str(cur_diff_res)]
            )


    if comp_res.isnotwrong () and max(exec_res) == 0 and max(diff_res) == 0:
        result_msg += "\nodevzdane reseni je spravne\n"
        res_code = 0
    else:
        result_msg += "\nodevzdane reseni je chybne:\n"
        res_code = 1
        if not comp_res.isnotwrong ():
            result_msg += "\tchyba pri kompilaci({}):\n{}\n".format (comp_res.exit, comp_res.error)
            res_code = 2

        if len (exec_res) and max (exec_res) != 0:
            result_msg += "\tchyba pri behu programu: kod ukonceni {:d}\n\t".format (max (exec_res))
            result_msg += "\n\t".join (errors)
            res_code = 3

        if len (diff_res) and max (diff_res) != 0:
            result_msg += "\tchybny vystup"
            res_code = 4

    result = {'exit': res_code, "outputs": outputs, 'suffix': RESULT_LETTER[str(res_code)], 'result': result_msg }
    return (result_file, result)

class TGHCheckDaemon(Daemon):

    def set_args (self, dir_to_watch, allow_root):
        self.dir_to_watch = dir_to_watch
        self.allow_root = allow_root

    def run(self):
        while True:
            jobs = os.listdir (self.dir_to_watch)
            print jobs
            for current_job in jobs:
                config_path = os.path.join (self.dir_to_watch, current_job, 'config.json')
                if os.path.exists (config_path) and os.path.isfile (config_path):
                    print config_path
                    try:
                        with open (config_path, 'r') as f:
                            config = json.load (f, encoding="utf-8")
                    except Exception as e:
                        print e

                    if config:
                        print 'valid job detected'
                        try:
                            (result_file, result) = process (config)
                            print result['result']
                            # write result
                            with open (result_file, 'w') as f:
                                json.dump (result, f, indent=True)
                            os.chmod (result_file, 0o666)
                        except Exception as e:
                            print e

                        # delete path as confirmation job is done
                        os.remove (config_path)
            time.sleep(2)

# su - tgh-worker -c "python /var/www/html/443/scripts/process.py start /home/jan-hybs/PycharmProjects/TGH-testing-server/443/jobs"
def usage (msg=None):
    if msg is not None:
        print msg
    print "usage: %s start|stop|restart dir_to_watch [--force]" % sys.argv[0]
    sys.exit(2)

if __name__ == "__main__":
    daemon = TGHCheckDaemon (pidfile='/tmp/tgh-runner.pid', name='TGH-Runner-D')
    argl = len(sys.argv)

    if argl < 2:
        usage()

    command = sys.argv[1]
    if command == 'start' or command == 'restart':
        if argl < 3:
            usage('specify directory to watch')
        else:
            dir_to_watch = sys.argv[2]

        if argl < 4:
            allow_root = False
        else:
            allow_root = sys.argv[3] == '--force'
        daemon.set_args (dir_to_watch, allow_root)


        print 'Running as "{}"'.format (getpass.getuser())
        print 'Watching dir "{}"'.format (dir_to_watch)

        if (os.getlogin() == 'root' or os.getuid() == 0) and allow_root is False:
            print 'You cannot run this daemon as root'
            print 'Use command su - <username> to run this daemon or add command --force if you are certain'
            sys.exit(1)

        if command == 'start':
            daemon.start()
        else:
            daemon.restart ()
        sys.exit(0)


    if command == 'stop':
        daemon.stop()
        sys.exit(0)

    if command == 'restart':
        daemon.restart ()
        sys.exit(0)




