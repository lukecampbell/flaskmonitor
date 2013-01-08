#!/usr/bin/env python
'''
@author Luke Campbell
@file flaskmonitor/process.py
'''

from gevent.event import Event
from gevent.queue import Queue

import gevent
import subprocess

from collections import namedtuple

process_stats = [
     '%cpu'       ,# percentage CPU usage (alias pcpu)
     '%mem'       ,# percentage memory usage (alias pmem)
     'acflag'     ,# accounting flag (alias acflg)
     'args'       ,# command and arguments
     'comm'       ,# command
     'command'    ,# command and arguments
     'cpu'        ,# short-term CPU usage factor (for scheduling)
     'etime'      ,# elapsed running time
     'flags'      ,# the process flags, in hexadecimal (alias f)
     'gid'        ,# processes group id (alias group)
     'inblk'      ,# total blocks read (alias inblock)
     'jobc'       ,# job control count
     'ktrace'     ,# tracing flags
     'ktracep'    ,# tracing vnode
     'lim'        ,# memoryuse limit
     'logname'    ,# login name of user who started the session
     'lstart'     ,# time started
     'majflt'     ,# total page faults
     'minflt'     ,# total page reclaims
     'msgrcv'     ,# total messages received (reads from pipes/sockets)
     'msgsnd'     ,# total messages sent (writes on pipes/sockets)
     'nice'       ,# nice value (alias ni)
     'nivcsw'     ,# total involuntary context switches
     'nsigs'      ,# total signals taken (alias nsignals)
     'nswap'      ,# total swaps in/out
     'nvcsw'      ,# total voluntary context switches
     'nwchan'     ,# wait channel (as an address)
     'oublk'      ,# total blocks written (alias oublock)
     'p_ru'       ,# resource usage (valid only for zombie)
     'paddr'      ,# swap address
     'pagein'     ,# pageins (same as majflt)
     'pgid'       ,# process group number
     'pid'        ,# process ID
     'ppid'       ,# parent process ID
     'pri'        ,# scheduling priority
     're'         ,# core residency time (in seconds; 127 = infinity)
     'rgid'       ,# real group ID
     'rss'        ,# resident set size
     'ruid'       ,# real user ID
     'ruser'      ,# user name (from ruid)
     'sess'       ,# session ID
     'sig'        ,# pending signals (alias pending)
     'sigmask'    ,# blocked signals (alias blocked)
     'sl'         ,# sleep time (in seconds; 127 = infinity)
     'start'      ,# time started
     'state'      ,# symbolic process state (alias stat)
     'svgid'      ,# saved gid from a setgid executable
     'svuid'      ,# saved UID from a setuid executable
     'tdev'       ,# control terminal device number
     'time'       ,# accumulated CPU time, user + system (alias cputime)
     'tpgid'      ,# control terminal process group ID
     'tsess'      ,# control terminal session ID
     'tsiz'       ,# text size (in Kbytes)
     'tt'         ,# control terminal name (two letter abbreviation)
     'tty'        ,# full name of control terminal
     'ucomm'      ,# name to be used for accounting
     'uid'        ,# effective user ID
     'upr'        ,# scheduling priority on return from system call (alias usrpri)
     'user'       ,# user name (from UID)
     'utime'      ,# user CPU time (alias putime)
     'vsz'        ,# virtual size in Kbytes (alias vsize)
     'wchan'      ,# wait channel (as a symbolic name)
     'wq'         ,# total number of workqueue threads
     'wqb'        ,# number of blocked workqueue threads
     'wqr'        ,# number of running workqueue threads
     'xstat'      ,# exit or stop status (valid only for stopped or zombie process)
     ]

ProcessStats = namedtuple('ProcessStats', process_stats[2:])

class ProcessCapture(object):
    process_id = 0
    rss        = list()
    mem        = list()
    cpu        = list()
    values     = 0
    command    = ""
    greenlet   = None
    done       = Event()

    
    def __init__(self,process_id):
        self.process_id = process_id
        command = subprocess.check_output(("ps -o command= -p %s" % process_id).split())
        self.command = command

    def start(self):
        self.done.clear()
        if not self.greenlet:
            self.greenlet = gevent.spawn(self.run)

    def run(self):
        while not self.done.wait(1):
            try:
                rss = self._stat('rss')
                mem = self._stat('%mem')
                cpu = self._stat('%cpu')
                self.rss.append(float(rss))
                self.mem.append(float(mem))
                self.cpu.append(float(cpu))
                self.values+=1
            except: 
                self.done.set()

    def stop(self):
        self.done.set()
        self.greenlet.join(2)
        self.greenlet.kill()
        self.greenlet = None

    def stats(self):
        stat_list = [self._stat(i) for i in process_stats[2:]]
        return ProcessStats(*stat_list)


    def _stat(self, v):
        s = subprocess.check_output(("ps -o %s= -p %s" %(v, self.process_id)).split())
        s = s.split('\n')[0]
        return s

        




def process_list():
    output = subprocess.check_output("ps -o pid,rss,%mem,%cpu,command -e -w".split())
    lines = output.split("\n")
    headers = lines[0].split()
    data = {}
    for header in headers:
        data[header] = []
    for line in lines[1:]:
        values = line.split()
        if values:
            data['PID'].append(values[0])
            data['RSS'].append(values[1])
            data['%MEM'].append(values[2])
            data['%CPU'].append(values[3])
            data['COMMAND'].append(" ".join(values[4:]))

    return data
        

        
