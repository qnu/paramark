#############################################################################
# ParaMark: A Benchmark for Parallel/Distributed Systems
# Copyright (C) 2009,2010  Nan Dun <dunnan@yl.is.s.u-tokyo.ac.jp>
# Distributed under GNU General Public Licence version 3
#n############################################################################

#
# modules/utils.py
# Common Constants, Routines and Utilities
#

import sys
import os
import errno
import time
import math

INTEGER_MAX = sys.maxint
INTEGER_MIN = -sys.maxint -1

KB = 1024
MB = 1048576
GB = 1073741824
TB = 1099511627776

VERBOSE_PROMPT = 0
VERBOSE_STAGE = 1
VERBOSE_ERROR = 2
VERBOSE_WARNING = 3
VERBOSE_INFO = 4
VERBOSE_DETAILS = 5

OPDATA_META = ["op", "nproc", "factor", "opcnt", "what"]
OPDATA_IO = ["op", "nproc", "fsize", "blksize", "what"]

if sys.platform == "win32":
    timer = time.clock
else:
    timer = time.time

def timer2():
    return time.localtime(), timer()

def ws(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def es(s):
    sys.stderr.write(s)

def parse_datasize(size):
    """ return the data size in bytes expressed by size string """
    size = size.upper()
    if size.isdigit():
        return eval(size)
    if size.endswith('B'):
        size = size[0:-1]
    if size.endswith('K'):
        return eval(size[0:-1]) * KB
    if size.endswith('M'):
        return eval(size[0:-1]) * MB
    if size.endswith('G'):
        return eval(size[0:-1]) * GB

def smart_datasize(size):
    """ given a size in bytes, return a tuple (num, unit) """
    size = float(size)
    if size < KB:
        return (size, "B")
    if size < MB:
        return (size/KB, "KB")
    if size < GB:
        return (size/MB, "MB")
    if size < TB:
        return (size/GB, "GB")
    return (size/TB, "TB")

def smart_makedirs(path, confirm=True):
    try: os.makedirs(path)
    except OSError, err:
        if err.errno == errno.EEXIST:
            sys.stderr.write("warning: directory %s exists\n" 
                % os.path.abspath(path))
            if confirm:
                ans = raw_input("Overwrite [Y/n/path]? ").lower()
                if ans == 'n':
                    sys.stderr.write("Aborting ...\n")
                    sys.exit(1)
                elif ans == "" or ans == 'y': pass
                else: return smart_makedirs(ans, confirm)
            else:
                sys.stderr.write("overwriting %s ...\n"
                    % os.path.abspath(path))
        else:
            sys.stderr.write("failed to create %s, %s\n" % \
                (path, os.strerror(err.errno)))
            sys.exit(1)
    return path

def string_hash(str):
    hashv = 0
    for i in range(0, len(str)):
        hashv = hashv + ord(str[i]) * (i + 1);
    return hashv

# Adapted from book Graphic Gems
# Chapter: Nice numbers for graph labels
#http://books.google.com/books?id=fvA7zLEFWZgC&pg=PA61&lpg=PA61#v=onepage&q=&f=false
def nicenum(x, round=True, logbase=10):
    """
    find a "nice" number approximately equal to x.
    Round the number if round = true, take ceiling if round = false
    """
    exp = math.floor(math.log(x, logbase)) # exponent of x
    f = x / math.pow(logbase, exp) # fractional part of x
    if round:
        if f < 1.5: nf = 1  # nice, rounded fraction
        elif f < 3: nf = 2
        elif f < 7: nf = 5
        else: nf = 10
    else:
        if f <= 1: nf = 1
        elif f <= 2: nf = 2
        elif f <= 5: nf = 5
        else: nf = 10
    return nf * math.pow(logbase, exp)

def loose_ticks(min, max, ntick=10):
    trange = nicenum(max - min, False)
    tinterval = nicenum(trange/(ntick - 1), True)
    tmin = math.floor(min/tinterval)*tinterval
    tmax = math.ceil(max/tinterval)*tinterval
    return tmin, tmax, tinterval

# list utilities
def list_unique(a):
    """ return the list with duplicate elements removed """
    return list(set(a))

def list_intersect(listoflist):
    """ return the intersection of a series of lists """
    inter = set(listoflist[0])
    for l in listoflist:
        inter = inter & set(l)
    return list(inter)

def list_union(listoflist):
    """ return the union of a series of lists """
    union = set(listoflist[0])
    for l in listoflist:
        union = union | set(l)
    return list(union)

def list_difference(listoflist):
    """ return the difference of a series of lists """
    diff = set(listoflist[0])
    for l in listoflist:
        diff = diff.difference(set(l))
    return list(set(diff))

def list_tostring(alist):
    """ return the list whose all elements converted to string """
    return map(lambda x:"%s" % x, alist)

# statistic functions
def stat_average(listofdata):
    """ return the average of a series of data """
    return sum(listofdata)/float(len(listofdata))

# scale funtion
#def smart_scale(minvalue, maxvalue):
#    """ return proper min/max/interval for axis """
#    return (vmin, vmax, vinterval)

# class init utility
def update_opts_kw(dict, restrict, opts, kw):
    """
    Update dict's value from opts and kw, restrict keyword in restrict
    """
    if opts is not None:
        for key in restrict:
            if dict.has_key(key) and opts.__dict__.has_key(key):
                dict[key] = opts.__dict__[key]

    if kw is not None:
        for key in restrict:
            if dict.has_key(key) and kw.has_key(key): dict[key] = kw[key]

# filesystem utility
def get_fs_info(path):
    """
    Get the mountpoint where the path belongs to
    """
    if sys.platform == "linux2":
        path = os.path.abspath(path)
        mountpoint = None
        fp = open("/etc/mtab", "r")
        for l in fp.readlines():
            if path.startswith(l.strip().split(" ")[1]):
                # TODO: startswith "/"
                mountpoint = l.strip()
        fp.close()
    elif sys.platform == "darwin":
        mountpoint = os.path.abspath(path)
    return mountpoint