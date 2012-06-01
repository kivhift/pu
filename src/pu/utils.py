#!/usr/bin/python
#
# Copyright (c) 2005-2012 Joshua Hughes <kivhift@gmail.com>
#
import datetime
import glob
import inspect
import itertools
import os
import Queue
import random
import re
import sys
import textwrap
import threading
import time
import traceback
import types

# Cache this for later.  It might be useful for restart() below.
cwd_at_import = os.getcwd()
def restart(start_cwd = None):
    '''
    This function is inspired by (i.e., purloined from) _do_execv in
    cherrypy.process.wspbus (v3.2).  It doesn't seem to work too well when
    running an interactive script that's started from a shell.  (They get
    into a fight over stdin.)

    User beware!  Make sure to clean up your loose ends.  You won't return
    from this function call.
    '''
    args = [sys.executable]
    for a in sys.argv:
        if a: args.append(a)
    if 'win32' == sys.platform: args = ['"%s"' % a for a in args]
    if start_cwd: os.chdir(start_cwd)
    os.execv(sys.executable, args)

def die(msg='', func=None, ecode=1, *args):
    """Print msg, call func and sys.exit with ecode.

Use func to print help, clean up, etc."""
    if len(args) > 0:
        msg += ': ' + ' '.join(map(str, args))

    if msg: print '\n', sandwich_wrap(msg)
    if func: func()
    sys.exit(ecode)

def warn(msg = '', *args):
    if len(args) > 0:
        msg += ': ' + ' '.join(map(str, args))

    if msg: print '\n', sandwich_wrap(msg)

def ddie(msg = '', *args):
    die(msg, None, 1, *args)

def sandwich_wrap(msg, wrapper = '-', width = 0):
    '''
    Wrap the given message in wrapper, repeating the wrapper as many times as
    needed to fill width.  If width is zero, then the terminal width (minus
    one) is used.
    '''
    if not width: width = cterm_rows_cols()[1] - 1
    mw = len(msg)
    if mw > width: mw = width
    wl = len(wrapper)
    if wl > 0:
        a, b = divmod(mw, wl)
        ew = wrapper * a + wrapper[:b]
        return '%s\n%s\n%s' % (ew,
            textwrap.fill(msg, width = mw, replace_whitespace = False), ew)
    else:
        return textwrap.fill(msg, width = mw, replace_whitespace = False)

def wrapped_paragraphs(lines, w):
    '''
    Given lines and width w, iteratively return the paragraphs with the lines
    wrapped to the width.
    '''
    for sep, li in itertools.groupby(lines.splitlines(True), key = str.isspace):
        if not sep:
            yield textwrap.fill(''.join(l.lstrip() for l in li), w)

# ActiveState Recipe # 577219
# http://code.activestate.com/recipes/577219-minimalistic-memoization/
def memoize(fn):
    cache = dict()
    def memoized_fn(*x):
        if x not in cache:
            cache[x] = fn(*x)
        return cache[x]
    return memoized_fn

def date_str(sep = os.sep, UTC = False, M = True, D = True, stamp = None):
    """Return a string with the given, or current, date (UTC?)
    separated with sep."""
    d = stamp
    if d is None:
        if UTC:
            d = time.gmtime()
        else:
            d = time.localtime()

    date = [d.tm_year]
    if M: date.append(d.tm_mon)
    if D: date.append(d.tm_mday)

    return sep.join(map(lambda n: '%02d' % n, date))

def y_str(UTC=False):
    """Returns a string with the current year (UTC?)"""
    return date_str(UTC=UTC, M=False, D=False)

def ym_str(sep=os.sep, UTC=False):
    """Returns a string with the current year & month (UTC?) with sep."""
    return date_str(sep=sep, UTC=UTC, D=False)

def ymd_str(sep=os.sep, UTC=False):
    """Return a string with the current date (UTC?) separated with sep."""
    return date_str(sep=sep, UTC=UTC)

def ymd_triplet(sep=os.sep, UTC=False):
    """Return an array with the year/mon/day in 0, 1, 2."""
    return date_str(sep=sep, UTC=UTC).split(sep)

def h_str(UTC=False):
    """Return a string with the current hour (UTC?)."""
    return time_str(UTC=UTC, M=False, S=False)

def hm_str(sep=os.sep, UTC=False):
    """Return a string with the current hour & minute (UTC?) separated
    with sep."""
    return time_str(sep=sep, UTC=UTC, S=False)

def hms_str(sep=os.sep, UTC=False):
    """Return a string with the current time (UTC?) separated with sep."""
    return time_str(sep=sep, UTC=UTC)

def time_str(sep = os.sep, UTC = False, M = True, S = True, stamp = None):
    """Return a string with the given, or current, time (UTC?)
    separated with sep."""
    t = stamp
    if t is None:
        if UTC:
            t = time.gmtime()
        else:
            t = time.localtime()

    tIme = [t.tm_hour]
    if M: tIme.append(t.tm_min)
    if S: tIme.append(t.tm_sec)

    return sep.join(map(lambda n: '%02d' % n, tIme))

def dt_str(sep = os.sep, UTC = False, stamp = None):
    """Return the given, or current, date+time (UTC?) separated with sep."""
    return sep.join([
        date_str(sep = sep, UTC = UTC, stamp = stamp),
        time_str(sep = sep, UTC = UTC, stamp = stamp)])

def utc_offset():
    """Return string for localtime's UTC offset.  Purloined from
    email/Utils.py"""
    now = time.localtime()

    if time.daylight and now[-1]:
        offset = time.altzone
    else:
        offset = time.timezone

    h, m = divmod(abs(offset), 3600)

    if offset > 0:
        sign = '-'
    else:
        sign = '+'

    return '%s%02d%02d' % (sign, h, m/60)

def ISO_8601_time_stamp():
    '''
    Return the current time, with time zone designator, in ISO 8601 format.
    '''
    ts = time.gmtime()
    return 'T'.join([date_str(sep = '-', stamp = ts),
        time_str(sep = ':', stamp = ts)]) + utc_offset()

def mkdir_and_cd(dir, mode=0755):
    """Make dir and cd into it.  Caller should handle exceptions."""
    os.mkdir(dir, mode)
    os.chdir(dir)

def mkdirs_and_cd(path, mode=0755):
    """Make all nonextant dirs on path and cd into final one."""
    os.makedirs(path, mode)
    os.chdir(path)

def cterm_rows_cols():
    """Returns the rows and columns of the controlling terminal."""
    # This function is adapted from code found here:
    # http://pdos.csail.mit.edu/~cblake/cls/cls.py
    # Since it uses fcntl and termios, it will only work under a Unix-type
    # OS.
    default_rc = (25, 80)
    try:
        if not sys.stdout.isatty():
            return default_rc
    except:
        return default_rc

    rows_cols = None
    try:
        import fcntl
        import struct
        import termios
        fd = os.open(os.ctermid(), os.O_RDONLY)
        rows_cols = struct.unpack('hh',
                fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        os.close(fd)
    except:
        rows_cols = None

    if not rows_cols:
        try:
            rows_cols = (os.env['LINES'], os.env['COLUMNS'])
        except:
            rows_cols = default_rc

    return int(rows_cols[0]), int(rows_cols[1])

def get_user_info():
    uinf = DataContainer(HOME = os.path.expanduser('~'))
    if uinf.HOME == '': return None

    osn = os.name
    if 'posix' == osn:
        uinf.update(EDITOR = os.getenv('EDITOR', 'vim'),
            SHELL = os.getenv('SHELL', 'bash'))
    elif 'nt' == osn:
        uinf.update(EDITOR = os.getenv('EDITOR', 'notepad.exe'),
            SHELL = os.getenv('SHELL', 'cmd.exe'))
    else:
        # Not sure what to do here?..
        return None

    return uinf

def get_app_data_dir(name):
    '''
    Return the conventional kitchen-drawer directory for the application named
    name.  Return None if confused.
    '''
    osn = os.name
    if 'posix' == osn:
        return os.path.join(get_user_info().HOME, '.' + name)
    elif 'nt' == osn:
        return os.path.join(os.environ['APPDATA'], name)

default_pw_size = 15
default_pw_chars = \
'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'

def generate_password(sz = default_pw_size, chars = default_pw_chars):
    '''Generate a random password using sz characters from chars.'''
    return ''.join([random.choice(chars) for i in xrange(sz)])

pppw_Ls = '`123456qwertasdfgzxcvb~!@#$%^QWERTASDFGZXCVB'
pppw_Rs = '7890-=yuiop[]\hjkl;\'nm,./&*()_+YUIOP{}|HJKL:"NM<>?'
def generate_pingpong_password(sz = default_pw_size,
        lchars = pppw_Ls, rchars = pppw_Rs):
    '''
    Generate a random password using sz characters from lchars and rchars,
    ping-ponging between the two.
    '''
    idx = random.sample([0, 1], 2)
    chars = [lchars, rchars]
    pwc = []
    for i in xrange(sz):
        pwc.append(random.choice(chars[idx[divmod(i, 2)[1]]]))

    return ''.join(pwc)

def generate_L_password(sz = default_pw_size, chars = pppw_Ls):
    '''
    Generate a random, left-handed password using sz characters from chars.
    '''

    return generate_password(sz = sz, chars = chars)

def generate_R_password(sz = default_pw_size, chars = pppw_Rs):
    '''
    Generate a random, right-handed password using sz characters from chars.
    '''

    return generate_password(sz = sz, chars = chars)

def copy_file(From, To, clobber=False):
    """Copy file From to file To.  If To is a directory, then From is
copied to To/From.  Raise exception if there's a problem"""

    if not os.path.isfile(From):
        raise TypeError, From + ' is not a regular file.'

    real_to = To
    if os.path.exists(real_to) and os.path.isdir(real_to):
        real_to = os.path.join(To, os.path.basename(From))
    if os.path.exists(real_to) and not clobber:
            raise IOError, real_to + ' exists and not clobbering.'

    blksize = 1024 * 8
    fromfile = open(From, 'rb')
    try:
        tofile = open(real_to, 'wb')
    except:
        fromfile.close()
        raise

    try:
        while 1:
            chunk = fromfile.read(blksize)
            if not chunk: break
            tofile.write(chunk)
    finally:
        fromfile.close()
        tofile.close()

def lineno():
    return inspect.currentframe().f_back.f_lineno

def function_name():
    return inspect.getframeinfo(inspect.currentframe().f_back)[2]

def caller_function_name():
    return inspect.getframeinfo(inspect.currentframe().f_back.f_back)[2]

def note_to_self(msg = ''):
    fi = inspect.getframeinfo(inspect.currentframe().f_back)
    print '[*] %s <%s:%s @ %d>' % (msg, os.path.basename(fi[0]),
        fi[2], fi[1])

class CheckedObject(object):
    '''
    Subclass this class (and possibly use checked_property()) to only allow
    an instance to set attributes that already exist.
    '''
    def __init__(self):
        super(CheckedObject, self).__init__()

    def __setattr__(self, name, value):
        if not hasattr(self, name) and '_checked_properties' != name:
            raise AttributeError('Setting new attributes not allowed.')
        super(CheckedObject, self).__setattr__(name, value)

def checked_property(name, description = None, default = None,
        is_valid = lambda val: True, xform = lambda val: val):
    def _check(s):
        if not hasattr(s, '_checked_properties'):
            s._checked_properties = {}
    def _get(s):
        _check(s)
        return s._checked_properties.get(name, default)
    def _set(s, val):
        if not is_valid(val):
            raise ValueError('Invalid %s given: %s.' % (
                description if description else name, str(val)))
        _check(s)
        v = xform(val)
        if default == v:
            if name in s._checked_properties:
                del s._checked_properties[name]
        else:
            s._checked_properties[name] = v
    def _del(s):
        _check(s)
        if name in s._checked_properties:
            del s._checked_properties[name]
    return property(_get, _set, _del, description)

def ranged_integer_checker(L, H):
    if not is_an_integer(L) or not is_an_integer(H) or L >= H:
        raise ValueError('Invalid integer range given: [%r, %r].' % (L, H))
    def _chk(val):
        return is_an_integer(val) and val >= L and val <= H
    _chk.minimum = L
    _chk.maximum = H
    return _chk

def ranged_float_checker(L, H):
    if type(L) is not float or type(H) is not float or L >= H:
        raise ValueError('Invalid float range given: [%r, %r].' % (L, H))
    def _chk(val):
        return type(val) is float and val >= L and val <= H
    _chk.minimum = L
    _chk.maximum = H
    return _chk

class ProgressIndicator(object):
    def __init__(self):
        super(ProgressIndicator, self).__init__()
        self.cancel = False

    def setStatusText(self, text):
        pass

    def setProgressRange(self, L, H):
        pass

    def incrementProgressValue(self):
        pass

    def setProgressValue(self, val):
        pass

    def doFunctionAndIncrement(self, text = '', fn = lambda : None,
            args = (), kwargs = {}):
        if self.cancel: return
        self.setStatusText(text)
        fn(*args, **kwargs)
        self.incrementProgressValue()

def contains_any(seq, aset):
    '''Check whether seq contains any of the items in aset. (PC2e:1.8)'''
    for c in seq:
        if c in aset: return True
    return False

def contains_only(seq, aset):
    '''Check whether seq contains only items in aset. (PC2e:1.8)'''
    for c in seq:
        if c not in aset: return False
    return True

def contains_all(seq, aset):
    '''Check whether seq contains all items in aset. (PC2e:1.8)'''
    return not set(aset).difference(seq)

def printf(fmt, *args):
    '''PC2e:4.20'''
    sys.stdout.write(fmt % args)

class Singleton(object):
    '''
    Inspired by recipe 6.15 in the "Python Cookbook, 2nd ed.".  There is only
    one instance and it's only initialized once if desired.  All the subclass
    has to do is Subclass.__init__ = Singleton._init_me_not somewhere in its
    __init__.
    '''
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)

        return cls._instance

    def _init_me_not(self, *args, **kwargs): pass

def curry(func, *a, **kw):
    '''Curry the given function with the given arguments. (PC2e:16.4)'''
    def curried(*xa, **xkw):
        return func(*(a + xa), **dict(kw, **xkw))
    curried.__name__ = func.__name__
    curried.__doc__ = func.__doc__
    curried.__dict__.update(func.__dict__)
    return curried

def directory_tree(basedir, padding = ' ', with_files = False):
    '''
    This is a modified version of code contributed by Doug Dahms on the
    ActiveState cookbook website.  It returns a string instead of printing the
    structure out.
    '''
    tree = '%s+-%s/' % (padding[:-1],
        os.path.basename(os.path.abspath(basedir)))
    padding += ' '

    if with_files:
        entries = os.listdir(basedir)
    else:
        entries = [ x for x in os.listdir(basedir)
            if os.path.isdir(os.path.join(basedir, x)) ]

    while entries:
        entry = entries.pop(0)
        path = os.path.join(basedir, entry)
        if os.path.isdir(path):
            tree += '\n%s' % directory_tree(
                path, padding + ('|' if entries else ' '), with_files)
        else:
            tree += '\n%s|-%s' % (padding, entry)

    return tree

def version_string2number(vs):
    ver_re = re.compile(
        r'^(?P<major>\d+)(?P<sep>\.|_)(?P<minor>\d+)(?P=sep)(?P<patch>\d+)$')

    m = ver_re.match(vs)
    if m is None:
        raise ValueError('Version string is not in correct format: %s' % vs)

    g = m.groupdict()
    ma, mi, pa = map(int, [g['major'], g['minor'], g['patch']])

    if ma > 0xff or mi > 0xff or pa > 0xff:
        raise ValueError('Version string produces number collision: %s' % vs)

    return (ma << 16) + (mi << 8) + pa

def random_bytes(length):
    return ''.join([chr(random.randint(0, 255)) for i in xrange(length)])
random_string = random_bytes

class DataContainer(object):
    '''
    This class can be used when one wants to easily pass a bunch of variables
    around quickly.  The typical object-based attribute lookup is available
    along with a mapping's key-based lookup; e.g., d.a and d['a'] are the same
    thing.
    '''
    def __init__(self, *args, **kwargs):
        super(DataContainer, self).__init__()

        L = len(args)
        if L > 1:
            raise TypeError(
                'DataContainer expected at most 1 argument, got %d' % L)
        self.update(*args, **kwargs)

    def __repr__(self):
        kwre = re.compile('^[_a-zA-Z][_a-zA-Z0-9]*$')
        kws, nonkws = [], []
        for k in sorted(self.keys()):
            if kwre.match(k):
                kws.append('%s = %r' % (k, getattr(self, k)))
            else:
                nonkws.append('%r : %r' % (k, getattr(self, k)))
        if nonkws: kws.insert(0, '{%s}' % ', '.join(nonkws))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(kws))

    def __contains__(self, item):
        return item in self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __delitem__(self, key):
        delattr(self, key)

    def __iter__(self):
        return self.__dict__.__iter__()

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def get(self, key, default = None):
        return self.__dict__.get(key, default)

    def clear(self):
        self.__dict__.clear()

    def setdefault(self, key, default = None):
        if hasattr(self, key): return getattr(self, key)
        setattr(self, key, default)
        return default

    def iterkeys(self):
        return self.__dict__.iterkeys()

    def itervalues(self):
        return self.__dict__.itervalues()

    def iteritems(self):
        return self.__dict__.iteritems()

    def copy(self):
        return self.__class__(self.__dict__.copy())

    def update(self, *args, **kw):
        L = len(args)
        if L > 1:
            raise TypeError('update expected at most 1 argument, got %d' % L)
        if 1 == L:
            other = args[0]
            if hasattr(other, 'keys') and callable(other.keys):
                for k in other:
                    setattr(self, k, other[k])
            else:
                for k, v in other:
                    setattr(self, k, v)
        for k in kw:
            setattr(self, k, kw[k])

def fn_with_retries(fn, limit, wait, reset_fn, *args, **kwargs):
    def fwr(*args, **kwargs):
        e = None
        for i in xrange(limit + 1):
            try:
                return fn(*args, **kwargs)
            except Exception, e:
                if wait > 0:
                    time.sleep(wait)
                reset_fn()
        raise e
    return fwr

def glimb(pattern, base = '.', all_matches = False):
    '''
    Search the given base directory and its super directories for path names
    matching the given pattern.  If all_matches is False, then the first-found
    match is returned.  Otherwise, all of the matches are returned as a list of
    path names.  If no matches are found, then None is returned.
    '''
    if not os.path.isdir(base):
        raise ValueError('Given base is not a directory: %s' % base)

    matches = []
    ap = os.path.abspath(base)
    last = ''
    while last != ap:
        matches.extend(glob.glob(os.path.join(ap, pattern)))
        if len(matches) > 0 and not all_matches: return matches[0]
        last = ap
        ap = os.path.dirname(ap)

    return matches if len(matches) > 0 else None

def rotn(s, n = 13):
    '''
    Perform a Caesar cipher on the given input string and return the
    result.  Only characters where .isalpha() is True are shifted.  The
    rest pass through to the output.
    '''
    orda = ord('a')
    ordA = ord('A')
    res = []
    for c in s:
        if c.isalpha():
            o = ord(c)
            off = ordA if o < orda else orda
            o -= off
            o += n
            o %= 26
            res.append(chr(o + off))
        else:
            res.append(c)
    return ''.join(res)

def rotn_cycle(s, sep = '\n', numbered = True):
    '''
    For the given input string, cycle through all 26 rotations and return
    them in a string, separated with sep and numbered by default.  If
    numbered is False, then the numbers are left out of the result.
    '''
    r = []
    for i in xrange(26):
        r.append('%s%s' % ('%02d ' % i if numbered else '', rotn(s, i)))
    return sep.join(r)

def import_code(code, name, doc = None, add_to_sys = False, globals_ = None):
    ''' This function is inspired by recipe 16.2, PCB 2nd ed.

    Returns a new module object initialized by importing the given code.
    If add_to_sys is True, then the new module is added to sys.modules with
    the given name.  Due to the use of exec, code can be a string, a
    file-like object or a compiled code object.
    '''
    module = types.ModuleType(name, doc)
    if add_to_sys: sys.modules[name] = module
    if globals_ is not None:
        exec code in globals_, module.__dict__
    else:
        exec code in module.__dict__
    return module

def is_an_integer(i):
    '''
    Returns True if the argument is a string, False otherwise.  See
    is_a_string() for the inspiration.
    '''
    return isinstance(i, (int, long))

def is_a_string(s):
    '''This is recipe 1.3, PCB 2nd ed.

    Returns True if the argument is a string, False otherwise.
    '''
    return isinstance(s, basestring)

def is_string_like(s):
    '''This is recipe 1.4, PCB 2nd ed.

    Returns True if the argument walks like a string, False otherwise.
    '''
    try:
        s + ''
        return True
    except:
        return False

class ThreadWithExceptionStatus(threading.Thread):
    '''
    This is simply threading.Thread with a Queue.Queue (in .status) that
    can be used to retrieve possible exceptions that occur whilst
    run()ning.  None will be put in the Queue if there are no exceptions.
    Otherwise, the exception information from sys.exc_info() is put in the
    Queue.  One can also pass the extra keyword argument exception_callback
    a function that takes no arguments that can be used to signal that an
    exception has occurred.  Giving a timeout in seconds will cause the
    thread execution to be delayed by that many seconds.  If delayed, the
    thread can be canceled via cancel.  The timeout stuff is adapted from
    _Timer() in the threading module in the standard library.
    '''
    def __init__(self, *a, **kwa):
        if 'exception_callback' in kwa:
            self.exc_callback = kwa.pop('exception_callback')
        else:
            self.exc_callback = lambda: None

        if 'timeout' in kwa:
            self.timeout = kwa.pop('timeout')
        else:
            self.timeout = 0.0

        super(ThreadWithExceptionStatus, self).__init__(*a, **kwa)
        self.status = Queue.Queue()
        self.finished = threading.Event()

    def cancel(self):
        self.finished.set()

    def run(self):
        try:
            self.finished.wait(self.timeout)
            if not self.finished.is_set():
                super(ThreadWithExceptionStatus, self).run()
                self.status.put(None)
            self.finished.set()
        except:
            self.status.put(sys.exc_info())
            self.exc_callback()

class LocalTimezoneInfo(datetime.tzinfo):
    '''
    This implementation is culled, with minor adjustments, from the
    documentation for the datetime module (v2.7.2).  The example section
    for the tzinfo base class contains this class and more.
    '''
    std_offset = datetime.timedelta(seconds = -time.timezone)
    dst_offset = (datetime.timedelta(seconds = -time.altzone)
        if time.daylight else std_offset)
    delta_dst_std = dst_offset - std_offset
    zero_delta = datetime.timedelta(0)

    def __repr__(self):
        return '%s.%s()' % (LocalTimezoneInfo.__module__,
            LocalTimezoneInfo.__name__)

    def utcoffset(self, dt):
        if self._is_dst(dt):
            return LocalTimezoneInfo.dst_offset
        else:
            return LocalTimezoneInfo.std_offset

    def dst(self, dt):
        if self._is_dst(dt):
            return LocalTimezoneInfo.delta_dst_std
        else:
            return LocalTimezoneInfo.zero_delta

    def tzname(self, dt):
        return time.tzname[self._is_dst(dt)]

    def _is_dst(self, dt):
        return time.localtime(time.mktime((dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second, dt.weekday(), 0, 0))).tm_isdst > 0

class FixedOffsetTimezoneInfo(datetime.tzinfo):
    '''
    Similar to LocalTimezoneInfo above, this implementation is taken from
    the tzinfo examples in the datetime module's documentation.
    '''
    zero_delta = datetime.timedelta(0)

    def __init__(self, offset = 0, name = 'UTC'):
        if not is_an_integer(offset):
            raise ValueError('offset should be an integer.')

        a_day = 24 * 60
        if offset <= -a_day or offset >= a_day:
            raise ValueError('abs(offset) is a day or more.')

        if not is_a_string(name):
            raise ValueError('name should be a string.')

        self.__offset = datetime.timedelta(minutes = offset)
        self.__name = name

    def __repr__(self):
        o = 24 * 60 * 60 * self.__offset.days + self.__offset.seconds
        return '%s.%s(%d, %r)' % (FixedOffsetTimezoneInfo.__module__,
            FixedOffsetTimezoneInfo.__name__, divmod(o, 60)[0], self.__name)

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return FixedOffsetTimezoneInfo.zero_delta

def byte_length(N):
    '''
    Return the number of bytes needed to represent the given non-negative
    integer N.
    '''
    if not is_an_integer(N):
        raise ValueError('N must be an integer: %r' % N)
    if N < 0:
        raise ValueError('N must be non-negative: %r' % N)

    blen = 0
    while N:
        blen += 1
        N >>= 8

    return blen

def script_is_frozen():
    '''Are we frozen via py2exe?'''
    return hasattr(sys, 'frozen')

def script_dir():
    '''
    Return the absolute path for the directory where the script resides
    adjusting for whether or not it's frozen.  See the py2exe wiki for the
    inspiration...
    '''
    fi = inspect.getframeinfo(inspect.currentframe().f_back)
    fname = sys.executable if script_is_frozen() else fi.filename
    return os.path.abspath(os.path.dirname(unicode(fname,
        sys.getfilesystemencoding())))

def condensed_traceback():
    '''
    Assuming that an exception has occured, this function returns a string that
    represents a condensed version of the last exception to occur with the
    following format:
        <exception text> @ <file name>:<line number>
    '''
    eT, eV, eTB = sys.exc_info()
    r = traceback.extract_tb(eTB)[-1]
    return '%s @ %s:%d' % (
        traceback.format_exception_only(eT, eV)[-1].strip(),
        os.path.basename(r[0]), r[1])
