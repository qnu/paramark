#############################################################################
# ParaMark: Benchmarking Suite for Parallel/Distributed Systems
# Copyright (C) 2009,2010  Nan Dun <dunnan@yl.is.s.u-tokyo.ac.jp>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################

#
# fs/opts.py
# Options and Configurations Parsers
#

import sys
import os
import stat

from modules.common import *
from modules.opts import Options as BaseOptions

class Options(BaseOptions):
    """
    Store/Retrieve options from/to configure files or command arguments
    """
    def __init__(self, argv=None):
        BaseOptions.__init__(self, argv)
        self.DEFAULT_CONFIG_STRING = FS_BENCHMARK_DEFAULT_CONFIG_STRING
    
    def _add_default_options(self):
        BaseOptions._add_default_options(self)

        def set_quickreport(option, opt_str, value, parser):
            parser.values.textreport = True
            parser.values.nolog = True
        
        # Should keep default value None here, since we need to test
        # whether an option has been set by command
        # instead, default values are set from DEFAULT_CONFIG_STRING
        self.optParser.add_option("-r", "--report", action="store", 
            type="string", dest="report", metavar="PATH", default=None, 
            help="generate report from log directory")
        
        self.optParser.add_option("-n", "--no-report", action="store_true",
            dest="noreport", default=False,
            help="do NOT report after benchmarking (default: disabled)")
        
        self.optParser.add_option("-w", "--wdir", action="store", 
            type="string", dest="wdir", metavar="PATH", default=None,
            help="working directory (default: cwd)")
        
        self.optParser.add_option("-l", "--logdir", action="store", 
            type="string", dest="logdir", metavar="PATH", default=None,
            help="log directory (default: auto)")
        
        self.optParser.add_option("-t", "--threads", action="store", 
            type="int", dest="nthreads", metavar="NUM", default=None,
            help="number of concurrent threads (default: 1)")
        
        self.optParser.add_option("-f", "--file", action="append",
            type="string", dest="use_files",metavar="PATH", default=None,
            help="files to use")
        
        self.optParser.add_option("--force", action="store_false",
            dest="confirm", default=True,
            help="force to go, do not confirm (default: disabled)")
        
        self.optParser.add_option("-q", "--quick-report", 
            action="callback", callback=set_quickreport,
            help="no log data, show text report only (default: disabled)")
        
        self.optParser.add_option("--text-report", action="store_true",
            dest="textreport", default=False,
            help="generate text report (default: disabled)")
        
        self.optParser.add_option("--csv-report", action="store_true",
            dest="csvreport", default=False,
            help="generate csv report (default: disabled)")
        
        self.optParser.add_option("--no-log", action="store_true",
            dest="nolog", default=False,
            help="do NOT save log, create report only (default: disabled)")
    
    def _valid_val(self, opt, val):
        from os import O_RDONLY, O_WRONLY, O_RDWR, O_APPEND,O_CREAT, \
            O_EXCL, O_TRUNC, O_DSYNC, O_RSYNC, O_SYNC, O_NDELAY, \
            O_NONBLOCK, O_NOCTTY, F_OK, R_OK, W_OK, X_OK
        from stat import S_ISUID, S_ISGID, S_ENFMT, S_ISVTX, \
            S_IREAD, S_IWRITE, S_IEXEC, S_IRWXU, S_IRUSR, S_IWUSR, \
            S_IXUSR, S_IRWXG, S_IRGRP, S_IWGRP, S_IXGRP, S_IRWXO, \
            S_IROTH, S_IWOTH, S_IXOTH
        from oper import OPS_META, OPS_IO
        
        if opt == "verbosity": return int(val)
        elif opt == "dryrun": return bool(eval(str(val)))
        elif opt == "nthreads": return int(val)
        elif opt == "confirm": return bool(val)
        elif opt == 'wdir': return os.path.abspath(val)
        elif opt == 'logdir':
            if val == "": return None
            else: return os.path.abspath(val)
        elif opt == "opcnt":
            return map(lambda v:int(v), val.split(','))
        elif opt == "factor":
            return map(lambda v:int(v), val.split(','))
        elif opt == "fsize":
            return map(lambda v:parse_datasize(v), val.split(','))
        elif opt == "bsize":
            return map(lambda v:parse_datasize(v), val.split(','))
        elif opt == "flags":
            if val.startswith("O_"): return eval(val)
            else: return str(val)
        elif opt == "mode":
            if val.startswith("S_") or val.startswith("F_"): 
                return eval(val)
            else: return str(val)
        elif opt == "meta":
            meta = []
            for m in val.split(','):
                m = m.strip().lower()
                if m in OPS_META: meta.append(m)
            if len(meta) > 0:
                meta.extend(['mkdir', 'rmdir'])
                meta = list_unique(meta)
                if len(meta) > 2: meta.extend(['creat', 'unlink'])
                meta = sorted(list_unique(meta), 
                    key=lambda o:OPS_META.index(o))
            return meta
        elif opt == "io":
            io = []
            for o in val.split(','):
                o = o.strip().lower()
                if o in OPS_IO: io.append(o)
            if len(io) > 0:
                #io.append('write')
                io = sorted(list_unique(io), key=lambda o:OPS_IO.index(o))
            return io
        elif opt == "fsync": return bool(eval(str(val)))
        elif opt == "times":
            if val == "": return None
        elif opt == "bufsize":
            if val == "": return -1
            else: return parse_datasize(val)
        return val
        
##########################################################################
# Default configure string
# Hard-coded for installation convenience
##########################################################################

FS_BENCHMARK_DEFAULT_CONFIG_STRING = """\
# ParaMark Default Benchmarking Configuration
# last updated: 2010/08/10

##########################################################################
# Howto:
#   * Only modify the values you would like to change.
#   * Lines beginning with '#' or ';' are ignored.
#   * Following the conventions of this file will be safe.
##########################################################################

##########################################################################
# Global Options
##########################################################################
[global]
# Benchmark working directory
wdir = ./

# Number of concurrent benchmarking thread
nthreads = 1

# Ask user whether to proceed on critical situations
confirm = True

# Verbosity level (0-5)
verbosity = 0

# Log directory of benchmarking results
# Generate a random log directory when logdir is not set
logdir =

# Metadata operations to be performed
# Does not support line continuation now, keep option in one line
# e.g.,
# meta = mkdir,rmdir,creat,access,open,open_close,stat_exist,stat_non,utime,chmod,rename,unlink
meta = 

# I/O operations to be performed
# e.g., 
# io = read,reread,write,rewrite,fread,freread,fwrite,frewrite
io = 

# Overwrite following local settings
override = True

# Variables to override
opcnt = 10
factor = 16

# File size and block size
# e.g., fsize=1K,2M,3G, bsize=1KB,2mb,3gb
fsize = 1M
bsize = 1K

# Report configuration

##########################################################################
# Local Operation Options
#   * Safe to leave alone
#   * Each operation in a seperate section
##########################################################################

#
# Options for flags
# O_RDONLY, O_WRONLY, RDWR, O_APPEND, O_CREAT, O_EXCL
# O_TRUNC or their inclusive OR
#
# Options for mode
# S_ISUID, S_ISGID, S_ENFMT, S_ISVTX, S_IREAD,
# S_IWRITE, S_IEXEC, S_IRWXU, S_IRUSR, S_IWUSR,
# S_IXUSR, S_IRWXG, S_IRGRP, S_IWGRP, S_IXGRP,
# S_IRWXO, S_IROTH, S_IWOTH, S_IXOTH or their bitwise OR
#

# Metadata operation
[mkdir]
opcnt = 0
factor = 16

[rmdir]
opcnt = 0
factor = 16

[creat]
opcnt = 0
factor = 16
flags = O_CREAT | O_WRONLY | O_TRUNC 
mode = S_IRUSR | S_IWUSR

[access]
opcnt = 0
# F_OK, R_OK, W_OK, X_OK or their inclusive OR
factor = 16
mode = F_OK

[open]
opcnt = 0
factor = 16
flags = O_RDONLY
mode = S_IRUSR

[open_close]
opcnt = 0
factor = 16
flags = O_RDONLY
mode = S_IRUSR

[stat_exist]
opcnt = 0
factor = 16

[stat_non]
opcnt = 0
factor = 16

[utime]
opcnt = 0
factor = 16
times =

[chmod]
opcnt = 0
factor = 16
mode = S_IEXEC

[rename]
opcnt = 0
factor = 16

[unlink]
opcnt = 0
factor = 16

# I/O operation
[read]
fsize = 0
bsize = 0
flags = O_RDONLY
mode = S_IRUSR

[reread]
fsize = 0
bsize = 0
flags = O_RDONLY
mode = S_IRUSR

[write]
fsize = 0
bsize = 0
flags = O_CREAT | O_RDWR
mode = S_IRUSR | S_IWUSR
fsync = False

[rewrite] 
fsize = 0
bsize = 0
flags = O_CREAT | O_RDWR
mode = S_IRUSR | S_IWUSR
fsync = False

[fread]
fsize = 0
bsize = 0
# 'r', 'w', 'a', 'b', '+', or their combinations
mode = r
bufsize = 

[freread]
fsize = 0
bsize = 0
mode = r
bufsize = 

[fwrite]
fsize = 0
bsize = 0
mode = w
bufsize = 
fsync = False

[frewrite]
fsize = 0
bsize = 0
mode = w
bufsize =
fsync = False
"""
