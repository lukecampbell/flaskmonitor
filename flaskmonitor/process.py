#!/usr/bin/env python
'''
@author Luke Campbell
@file flaskmonitor/process.py
'''

from gevent.event import Event

import gevent
import sys
import subprocess

from collections import namedtuple

process_stats_mac = [
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

process_stats_linux = [
'%cpu', #       %CPU     cpu utilization of the process in "##.#" format. Currently, it is the CPU time used divided 
        #                by the time the process has been running (cputime/realtime ratio), expressed as a percentage. 
        #                It will not add up to 100% unless you are lucky. (alias pcpu).
'%mem', #       %MEM     ratio of the process’s resident set size  to the physical memory on the machine, expressed as 
        #                a percentage. (alias pmem).
'args', #       COMMAND  command with all its arguments as a string. Modifications to the arguments may be shown. The 
        #                output in this column may contain spaces. A process marked <defunct> is partly dead, waiting 
        #                to be fully destroyed by its parent. Sometimes the process args will be unavailable; when 
        #                this happens, ps will instead print the executable name in brackets. (alias cmd, command). 
        #                See also the comm format keyword, the -f option, and the c option.  When specified last, this 
        #                column will extend to the edge of the display. If ps can not determine display width, as when 
        #                output is redirected (piped) into a file or another command, the output width is undefined. (
        #                it may be 80, unlimited, determined by the TERM variable, and so on) The COLUMNS environment 
        #                variable or --cols option may be used to exactly determine the width in this case. The w or 
        #                -w option may be also be used to adjust width.
'blocked', #    BLOCKED  mask of the blocked signals, see signal(7). According to the width of the field, a 32-bit or 
           #             64-bit mask in hexadecimal format is displayed.  (alias sig_block, sigmask).
'bsdstart', #   START    time the command started. If the process was started less than 24 hours ago, the output format 
            #            is " HH:MM", else it is "mmm dd" (where mmm is the three letters of the month). See also 
            #            lstart, start, start_time, and stime.
'bsdtime', #    TIME     accumulated cpu time, user + system. The display format is usually "MMM:SS", but can be 
           #             shifted to the right if the process used more than 999 minutes of cpu time.
'c', #          C        processor utilization. Currently, this is the integer value of the percent usage over the 
     #                   lifetime of the process. (see %cpu).
'caught', #     CAUGHT   mask of the caught signals, see signal(7). According to the width of the field, a 32 or 64 
          #              bits mask in hexadecimal format is displayed.  (alias sig_catch, sigcatch).
'cgroup', #     CGROUP   display control groups to which the process belonges.
'class', #      CLS      scheduling class of the process. (alias policy, cls). Field’s possible values are:
         #                    -   not reported
         #                    TS  SCHED_OTHER
         #                    FF  SCHED_FIFO
         #                    RR  SCHED_RR
         #                    B   SCHED_BATCH
         #                    ISO SCHED_ISO
         #                    IDL SCHED_IDLE
         #                    ?   unknown value
'cls',   #      CLS      scheduling class of the process. (alias policy, class). Field’s possible values are:
         #                    -   not reported
         #                    TS  SCHED_OTHER
         #                    FF  SCHED_FIFO
         #                    RR  SCHED_RR
         #                    B   SCHED_BATCH
         #                    ISO SCHED_ISO
         #                    IDL SCHED_IDLE
         #                    ?   unknown value
'cmd',   #      CMD      see args. (alias args, command).
'comm',  #      COMMAND  command name (only the executable name). Modifications to the command name will not be shown. 
         #               A process marked <defunct> is partly dead, waiting to be fully destroyed by its parent. The 
         #               output in this column may contain spaces. (alias ucmd, ucomm). See also the args format 
         #               keyword, the -f option, and the c option.  When specified last, this column will extend to the 
         #               edge of the display. If ps can not determine display width, as when output is redirected (
         #               piped) into a file or another command, the output width is undefined. (it may be 80, 
         #               unlimited, determined by the TERM variable, and so on) The COLUMNS environment variable or 
         #               --cols option may be used to exactly determine the width in this case. The w or -w option 
         #               may be also be used to adjust width.  
'command', #    COMMAND  see args. (alias args, cmd).
'cp',      #    CP       per-mill (tenths of a percent) CPU usage. (see %cpu).
'cputime', #    TIME     cumulative CPU time, "[dd-]hh:mm:ss" format. (alias time).
'egid', #       EGID     effective group ID number of the process as a decimal integer. (alias gid).
'egroup', #     EGROUP   effective group ID of the process. This will be the textual group ID, if it can be obtained 
          #              and the field width permits, or a decimal representation otherwise. (alias group).
'eip', #        EIP      instruction pointer.
'esp', #        ESP      stack pointer.
'etime', #      ELAPSED  elapsed time since the process was started, in the form [[dd-]hh:]mm:ss.
'euid', #       EUID     effective user ID. (alias uid).
'euser', #      EUSER    effective user name. This will be the textual user ID, if it can be obtained and the field 
         #               width permits, or a decimal representation otherwise. The n option can be used to force the 
         #               decimal representation. (alias uname, user).
'f', #          F        flags associated with the process, see the PROCESS FLAGS section. (alias flag, flags).
'fgid', #       FGID     filesystem access group ID. (alias fsgid).
'fgroup', #     FGROUP   filesystem access group ID. This will be the textual user ID, if it can be obtained and the 
          #              field width permits, or a decimal representation otherwise.  (alias fsgroup).
'flag', #       F        see f. (alias f, flags).
'flags', #      F        see f. (alias f, flag).
'fname', #      COMMAND  first 8 bytes of the base name of the process’s executable file. The output in this column may 
         #               contain spaces.
'fuid', #       FUID     filesystem access user ID. (alias fsuid).
'fuser', #      FUSER    filesystem access user ID. This will be the textual user ID, if it can be obtained and the 
         #               field width permits, or a decimal representation otherwise.
'gid', #        GID      see egid. (alias egid).
'group', #      GROUP    see egroup. (alias egroup).
'ignored', #    IGNORED  mask of the ignored signals, see signal(7). According to the width of the field, a 32-bit or 64-bit mask in hexadecimal format is displayed. (alias sig_ignore, sigignore).
'label', #      LABEL    security label, most commonly used for SE Linux context data. This is for the Mandatory Access Control ("MAC") found on high-security systems.
'lstart', #     STARTED  time the command started. See also bsdstart, start, start_time, and stime.
'lwp', #        LWP      lwp (light weight process, or thread) ID of the lwp being reported. (alias spid, tid).
'ni', #         NI       nice value. This ranges from 19 (nicest) to -20 (not nice to others), see nice(1). (alias nice).
'nice', #       NI       see ni. (alias ni).
'nlwp', #       NLWP     number of lwps (threads) in the process. (alias thcount).
'nwchan', #     WCHAN    address of the kernel function where the process is sleeping (use wchan if you want the kernel function name). Running tasks will display a dash (’-’) in this column.
'pcpu', #       %CPU     see %cpu. (alias %cpu).
'pending', #    PENDING  mask of the pending signals. See signal(7). Signals pending on the process are distinct from signals pending on individual threads. Use the m option or the -m option to see both. According to the width of the field, a 32-bit or 64-bit mask in hexadecimal format is displayed. (alias sig).
'pgid', #       PGID     process group ID or, equivalently, the process ID of the process group leader. (alias pgrp).
'pgrp', #       PGRP     see pgid. (alias pgid).
'pid', #        PID      process ID number of the process.
'pmem', #       %MEM     see %mem. (alias %mem).
'policy', #     POL      scheduling class of the process. (alias class, cls). Possible values are:
          #                   -   not reported
          #                   TS  SCHED_OTHER
          #                   FF  SCHED_FIFO
          #                   RR  SCHED_RR
          #                   B   SCHED_BATCH
          #                   ISO SCHED_ISO
          #                   IDL SCHED_IDLE
          #                   ?   unknown value
'ppid', #       PPID     parent process ID.
'psr', #        PSR      processor that process is currently assigned to.
'rgid', #       RGID     real group ID.
'rgroup', #     RGROUP   real group name. This will be the textual group ID, if it can be obtained and the field width permits, or a decimal representation otherwise.
'rip', #        RIP      64-bit instruction pointer.
'rsp', #        RSP      64-bit stack pointer.
'rss', #        RSS      resident set size, the non-swapped physical memory that a task has used (in kiloBytes). (alias rssize, rsz).
'rssize', #     RSS      see rss. (alias rss, rsz).
'rsz', #        RSZ      see rss. (alias rss, rssize).
'rtprio', #     RTPRIO   realtime priority.
'ruid', #       RUID     real user ID.
'ruser', #      RUSER    real user ID. This will be the textual user ID, if it can be obtained and the field width permits, or a decimal representation otherwise.
's', #          S        minimal state display (one character). See section PROCESS STATE CODES for the different values. See also stat if you want additional information displayed. (alias state).
'sched', #      SCH      scheduling policy of the process. The policies SCHED_OTHER (SCHED_NORMAL), SCHED_FIFO, SCHED_RR, SCHED_BATCH, SCHED_ISO, and SCHED_IDLE are respectively displayed as 0, 1, 2, 3, 4, and 5.
'sess', #       SESS     session ID or, equivalently, the process ID of the session leader. (alias session, sid).
'sgi_p', #      P        processor that the process is currently executing on. Displays "*" if the process is not currently running or runnable.
'sgid', #       SGID     saved group ID. (alias svgid).
'sgroup', #     SGROUP   saved group name. This will be the textual group ID, if it can be obtained and the field width permits, or a decimal representation otherwise.
'sid', #        SID      see sess. (alias sess, session).
'sig', #        PENDING  see pending. (alias pending, sig_pend).
'sigcatch', #   CAUGHT   see caught. (alias caught, sig_catch).
'sigignore', #  IGNORED  see ignored. (alias ignored, sig_ignore).
'sigmask', #    BLOCKED  see blocked. (alias blocked, sig_block).
'size', #       SZ       approximate amount of swap space that would be required if the process were to dirty all writable pages and then be swapped out. This number is very rough!
'spid', #       SPID     see lwp. (alias lwp, tid).
'stackp', #     STACKP   address of the bottom (start) of stack for the process.
'start', #      STARTED  time the command started. If the process was started less than 24 hours ago, the output format is "HH:MM:SS", else it is "  mmm dd" (where mmm is a three-letter month name). See also lstart, bsdstart, start_time, and stime.
'start_time', # START    starting time or date of the process. Only the year will be displayed if the process was not started the same year ps was invoked, or "mmmdd" if it was not started the same day, or "HH:MM" otherwise. See also bsdstart, start, lstart, and stime.
'stat', #       STAT     multi-character process state. See section PROCESS STATE CODES for the different values meaning. See also s and state if you just want the first character displayed.
'state', #      S        see s. (alias s).
'suid', #       SUID     saved user ID. (alias svuid).
'suser', #      SUSER    saved user name. This will be the textual user ID, if it can be obtained and the field width permits, or a decimal representation otherwise.  (alias svuser).
'svgid', #      SVGID    see sgid. (alias sgid).
'svuid', #      SVUID    see suid. (alias suid).
'sz', #         SZ       size in physical pages of the core image of the process. This includes text, data, and stack space. Device mappings are currently excluded; this is subject to change. See vsz and rss.
'thcount', #    THCNT    see nlwp. (alias nlwp). number of kernel threads owned by the process.
'tid', #        TID      see lwp. (alias lwp).
'time', #       TIME     cumulative CPU time, "[dd-]hh:mm:ss" format. (alias cputime).
'tname', #      TTY      controlling tty (terminal). (alias tt, tty).
'tpgid', #      TPGID    ID of the foreground process group on the tty (terminal) that the process is connected to, or -1 if the process is not connected to a tty.
'tt', #         TT       controlling tty (terminal). (alias tname, tty).
'tty', #        TT       controlling tty (terminal). (alias tname, tt).
'ucmd', #       CMD      see comm. (alias comm, ucomm).
'ucomm', #      COMMAND  see comm. (alias comm, ucmd).
'uid', #        UID      see euid. (alias euid).
'uname', #      USER     see euser. (alias euser, user).
'user', #       USER     see euser. (alias euser, uname).
'vsize', #      VSZ      see vsz. (alias vsz).
'vsz', #        VSZ      virtual memory size of the process in KiB (1024-byte units). Device mappings are currently excluded; this is subject to change. (alias vsize).
'wchan', #      WCHAN    name of the kernel function in which the process is sleeping, a "-" if the process is running, or a "*" if the process is multi-threaded and ps is not displaying threads.

        ]

if 'darwin' in sys.platform:
    process_stats = process_stats_mac
elif 'linux2' in sys.platform:
    process_stats = process_stats_linux
else:
    raise Exception('%s is not a currently supported platform.' % sys.platform)

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
        

        
