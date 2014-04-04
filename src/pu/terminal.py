#
# Copyright (c) 2006-2014 Joshua Hughes <kivhift@gmail.com>
#
from __future__ import print_function
import os
import sys

class _TerminalBase(object):
    def __init__(self):
        super(_TerminalBase, self).__init__()

        self.so = sys.stdout
        self.is_term = False
        self.default_R_and_C = (25, 80)

    def _setup_color(self):
        if self.is_term:
            self.black = (lambda t: self.ctext(t, 'fg_black'))
            self.bold_black = (lambda t: self.ctext(t,
                'fg_black', 'bg_default', 'bold'))
            self.red = (lambda t: self.ctext(t, 'fg_red'))
            self.bold_red = (lambda t: self.ctext(t,
                'fg_red', 'bg_default', 'bold'))
            self.green = (lambda t: self.ctext(t, 'fg_green'))
            self.bold_green = (lambda t: self.ctext(t,
                'fg_green', 'bg_default', 'bold'))
            self.yellow = (lambda t: self.ctext(t, 'fg_yellow'))
            self.bold_yellow = (lambda t: self.ctext(t,
                'fg_yellow', 'bg_default', 'bold'))
            self.blue = (lambda t: self.ctext(t, 'fg_blue'))
            self.bold_blue = (lambda t: self.ctext(t,
                'fg_blue', 'bg_default', 'bold'))
            self.magenta = (lambda t: self.ctext(t, 'fg_magenta'))
            self.bold_magenta = (lambda t: self.ctext(t,
                'fg_magenta', 'bg_default', 'bold'))
            self.cyan = (lambda t: self.ctext(t, 'fg_cyan'))
            self.bold_cyan = (lambda t: self.ctext(t,
                'fg_cyan', 'bg_default', 'bold'))
            self.white = (lambda t: self.ctext(t, 'fg_white'))
            self.bold_white = (lambda t: self.ctext(t,
                'fg_white', 'bg_default', 'bold'))
        else:
            self.black = self.nctext
            self.bold_black = self.nctext
            self.red = self.nctext
            self.bold_red = self.nctext
            self.green = self.nctext
            self.bold_green = self.nctext
            self.yellow = self.nctext
            self.bold_yellow = self.nctext
            self.blue = self.nctext
            self.bold_blue = self.nctext
            self.magenta = self.nctext
            self.bold_magenta = self.nctext
            self.cyan = self.nctext
            self.bold_cyan = self.nctext
            self.white = self.nctext
            self.bold_white = self.nctext

    def nctext(self, txt):
        '''Pass txt through to stdout.'''
        self.so.write(txt)

    def ctext(self, txt='', fg='fg_default', bg='bg_default', *attr):
        raise NotImplementedError('ctext')

    def title(self, title):
        raise NotImplementedError('title')

    def clear_and_home(self):
        raise NotImplementedError('clear_and_home')

    def rows_and_cols(self):
        raise NotImplementedError('rows_and_cols')

    def _exercise(self):
        self.clear_and_home()
        self.nctext('Rows & Cols: %s\n' % str(self.rows_and_cols()))
        self.ctext('Orbis, te saluto!\n', 'fg_black', 'bg_green')
        self.ctext('Hello, world!\n', 'fg_white', 'bg_blue')
        self.black('black\n')
        self.bold_black('bold_black\n')
        self.red('red\n')
        self.bold_red('bold_red\n')
        self.green('green\n')
        self.bold_green('bold_green\n')
        self.yellow('yellow\n')
        self.bold_yellow('bold_yellow\n')
        self.blue('blue\n')
        self.bold_blue('bold_blue\n')
        self.magenta('magenta\n')
        self.bold_magenta('bold_magenta\n')
        self.cyan('cyan\n')
        self.bold_cyan('bold_cyan\n')
        self.white('white\n')
        self.bold_white('bold_white\n')
        self.title('terminal.py was here...')

class _ANSITerm(_TerminalBase):
    def __init__(self):
        super(_ANSITerm, self).__init__()

        self.is_term = ('posix' == os.name and self.so.isatty())

        self.__esc = "\x1b["

        self.__seq = seq = {}
        seq["normal"]       = '00'
        seq["bold"]         = '01'
        seq["faint"]        = '02'
        seq["standout"]     = '03'
        seq["underline"]    = '04'
        seq["blink"]        = '05'
        seq["reverse"]      = '07'
        seq["fg_black"]     = '30'
        seq["fg_red"]       = '31'
        seq["fg_green"]     = '32'
        seq["fg_yellow"]    = '33'
        seq["fg_blue"]      = '34'
        seq["fg_magenta"]   = '35'
        seq["fg_cyan"]      = '36'
        seq["fg_white"]     = '37'
        seq["fg_default"]   = '39'
        seq["bg_black"]     = '40'
        seq["bg_red"]       = '41'
        seq["bg_green"]     = '42'
        seq["bg_yellow"]    = '43'
        seq["bg_blue"]      = '44'
        seq["bg_magenta"]   = '45'
        seq["bg_cyan"]      = '46'
        seq["bg_white"]     = '47'
        seq["bg_default"]   = '49'

        self.__reset = self.__esc + seq['normal'] + 'm'

        self.__legal_terms = ["xterm", "Eterm", "aterm", "rxvt",
                "screen", "kterm", "rxvt-unicode", "cygwin"]

        self._setup_color()

    def ctext(self, txt='', fg='fg_default', bg='bg_default', *attr):
        if not self.is_term:
            self.nctext(txt)
            return

        seq = self.__seq
        tmp = self.__esc + seq[fg] + ';' + seq[bg]
        for x in attr:
            tmp += ';' + seq[x]
        self.so.write(tmp + 'm' + txt + self.__esc + self.__reset)

    def title(self, title):
        if 'posix' == os.name \
                and sys.stderr.isatty() \
                and os.environ.has_key('TERM'):
            term = os.environ['TERM']
            if (term in self.__legal_terms) or term.startswith("xterm"):
                sys.stderr.write("\x1b]2;" + title + "\x07")
                sys.stderr.flush()
            elif term.startswith("screen"):
                sys.stderr.write("\x1b]2;" + title + "\x07")
                sys.stderr.write("\x1bk" + title + "\x1b\\")
                sys.stderr.flush()

    def clear_and_home(self):
        if self.is_term: self.so.write('\x1b[2J\x1b[H\x1b[0m')

    def rows_and_cols(self):
        """Returns the rows and columns of the controlling terminal."""
        # This function is adapted from code found here:
        # http://pdos.csail.mit.edu/~cblake/cls/cls.py Since it uses
        # fcntl and termios, it will only work under a Unix-type OS.

        if not self.is_term: return self.default_R_and_C

        rows_cols = None
        try:
            import fcntl
            import struct
            import termios
            fd = os.open(os.ctermid(), os.O_RDONLY)
            rows_cols = struct.unpack('hh', fcntl.ioctl(fd,
                termios.TIOCGWINSZ, '1234'))
            os.close(fd)
        except:
            rows_cols = None

        if not rows_cols:
            try:
                rows_cols = (os.env['LINES'], os.env['COLUMNS'])
            except:
                rows_cols = (25, 80)

        return int(rows_cols[0]), int(rows_cols[1])

if 'nt' == os.name:
    try:
        import ctypes
        import ctypes.wintypes
        if not hasattr(ctypes.wintypes, 'COORD'):
            ctypes.wintypes.COORD = ctypes.wintypes._COORD

        class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
            _fields_ = [
                ('dwSize', ctypes.wintypes.COORD),
                ('dwCursorPosition', ctypes.wintypes.COORD),
                ('wAttributes', ctypes.wintypes.WORD),
                ('srWindow', ctypes.wintypes.SMALL_RECT),
                ('dwMaximumWindowSize', ctypes.wintypes.COORD)
                ]
    except ImportError:
        print("Couldn't find the ctypes module. Sorry, no color.",
            file = sys.stderr)

class _Win32Term(_TerminalBase):
    def __init__(self):
        super(_Win32Term, self).__init__()

        # See the M$ website (or MSDN) for info. on these values.
        STDIN_HANDLE = -10
        STDOUT_HANDLE = -11
        STDERR_HANDLE = -12
        INVALID_HANDLE_VALUE = -1
        # foreground color and intensity
        FG_B = 0x01
        FG_G = 0x02
        FG_R = 0x04
        FG_I = 0x08
        FG_M = 0x0f
        # background color and intensity
        BG_B = 0x10
        BG_G = 0x20
        BG_R = 0x40
        BG_I = 0x80
        BG_M = 0xf0

        self.is_term = ('nt' == os.name
                and self.so.isatty()
                and 'ctypes' in globals())

        self.__seq = seq = {}
        seq["normal"]       = 0
        seq["bold"]         = FG_I
        seq["faint"]        = 0
        seq["standout"]     = 0
        seq["underline"]    = 0
        seq["blink"]        = 0
        seq["reverse"]      = 0
        seq["fg_bold"]      = FG_I
        seq["fg_black"]     = 0
        seq["fg_red"]       = FG_R
        seq["fg_green"]     = FG_G
        seq["fg_yellow"]    = FG_R | FG_G
        seq["fg_blue"]      = FG_B
        seq["fg_magenta"]   = FG_R | FG_B
        seq["fg_cyan"]      = FG_G | FG_B
        seq["fg_white"]     = FG_R | FG_G | FG_B
        seq["fg_default"]   = FG_R | FG_G | FG_B
        seq["bg_bold"]      = BG_I
        seq["bg_black"]     = 0
        seq["bg_red"]       = BG_R
        seq["bg_green"]     = BG_G
        seq["bg_yellow"]    = BG_R | BG_G
        seq["bg_blue"]      = BG_B
        seq["bg_magenta"]   = BG_R | BG_B
        seq["bg_cyan"]      = BG_G | BG_B
        seq["bg_white"]     = BG_R | BG_G | BG_B
        seq["bg_default"]   = 0
        seq["default"]      = FG_R | FG_G | FG_B

        if self.is_term:
            k32 = ctypes.windll.kernel32
            self.soh = soh = k32.GetStdHandle(STDOUT_HANDLE)
            if not soh or (INVALID_HANDLE_VALUE == soh):
                raise RuntimeError('Unable to get standard handle.')

            csbi = CONSOLE_SCREEN_BUFFER_INFO()
            if 0 == k32.GetConsoleScreenBufferInfo(soh, ctypes.byref(csbi)):
                raise RuntimeError('Unable to get console screen buffer info.')
            seq["default"] = csbi.wAttributes
            seq["fg_default"] = csbi.wAttributes & FG_M
            seq["bg_default"] = csbi.wAttributes & BG_M

        self._setup_color()

    def __del__(self):
        ctypes.windll.kernel32.SetConsoleTextAttribute(self.soh,
            self.__seq['default'])
        super(_Win32Term, self).__del__()

    def ctext(self, txt='', fg='fg_default', bg='bg_default', *attr):
        if not self.is_term:
            self.nctext(txt)
            return

        soh, seq, k32 = self.soh, self.__seq, ctypes.windll.kernel32

        c = seq[fg] | seq[bg]
        for x in attr: c |= seq[x]

        dc = seq['default']

        if 0 == k32.SetConsoleTextAttribute(soh, c):
            raise RuntimeError('Could not set text attribute.')
        self.so.write(txt)
        if 0 == k32.SetConsoleTextAttribute(soh, dc):
            raise RuntimeError('Could not set text attribute to default.')

    def title(self, title):
        if not self.is_term: return

        t = ctypes.c_char_p(title)
        if 0 == ctypes.windll.kernel32.SetConsoleTitleA(t):
            raise RuntimeError('Had trouble setting console title.')

    def clear_and_home(self):
        if not self.is_term: return

        soh, k32, wt = self.soh, ctypes.windll.kernel32, ctypes.wintypes

        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        if 0 == k32.GetConsoleScreenBufferInfo(soh, ctypes.byref(csbi)):
            raise RuntimeError('Could not get console screen buffer info.')

        con_size = wt.DWORD(csbi.dwSize.X * csbi.dwSize.Y)

        homepos = wt.COORD(0, 0)
        chars_written = wt.DWORD(0)

        if 0 == k32.FillConsoleOutputCharacterA(soh, ctypes.c_char(' '),
                con_size, homepos, ctypes.byref(chars_written)):
            raise RuntimeError('Had trouble filling console with blanks.')
        if con_size.value != chars_written.value:
            raise RuntimeError('Blanks underwritten: {} != {}'.format(
                con_size.value, chars_written.value))

        if 0 == k32.FillConsoleOutputAttribute(soh, csbi.wAttributes, con_size,
                homepos, ctypes.byref(chars_written)):
            raise RuntimeError('Had trouble setting console attributes.')
        if con_size.value != chars_written.value:
            raise RuntimeError('Attributes underwritten: {} != {}'.format(
                con_size.value, chars_written.value))

        if 0 == k32.SetConsoleCursorPosition(soh, homepos):
            raise RuntimeError('Had trouble homing cursor.')

    def rows_and_cols(self):
        if not self.is_term: return self.default_R_and_C

        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        if 0 == ctypes.windll.kernel32.GetConsoleScreenBufferInfo(self.soh,
                ctypes.byref(csbi)):
            raise RuntimeError('Could not get console screen buffer info.')

        R = csbi.srWindow.Bottom - csbi.srWindow.Top + 1
        C = csbi.srWindow.Right - csbi.srWindow.Left + 1

        return R, C

# _ANSITerm explicitly only supports os.name == 'posix'.  But, if it's not, it
# will only be slightly lame and not dead.
Terminal = _Win32Term if os.name == 'nt' else _ANSITerm
