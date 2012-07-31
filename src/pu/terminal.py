#
# Copyright (c) 2006-2012 Joshua Hughes <kivhift@gmail.com>
#
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

        self.__seq = {}
        self.__seq["normal"]       = '00'
        self.__seq["bold"]         = '01'
        self.__seq["faint"]        = '02'
        self.__seq["standout"]     = '03'
        self.__seq["underline"]    = '04'
        self.__seq["blink"]        = '05'
        self.__seq["reverse"]      = '07'
        self.__seq["fg_black"]     = '30'
        self.__seq["fg_red"]       = '31'
        self.__seq["fg_green"]     = '32'
        self.__seq["fg_yellow"]    = '33'
        self.__seq["fg_blue"]      = '34'
        self.__seq["fg_magenta"]   = '35'
        self.__seq["fg_cyan"]      = '36'
        self.__seq["fg_white"]     = '37'
        self.__seq["fg_default"]   = '39'
        self.__seq["bg_black"]     = '40'
        self.__seq["bg_red"]       = '41'
        self.__seq["bg_green"]     = '42'
        self.__seq["bg_yellow"]    = '43'
        self.__seq["bg_blue"]      = '44'
        self.__seq["bg_magenta"]   = '45'
        self.__seq["bg_cyan"]      = '46'
        self.__seq["bg_white"]     = '47'
        self.__seq["bg_default"]   = '49'

        self.__reset = self.__esc + self.__seq['normal'] + 'm'

        self.__legal_terms = ["xterm", "Eterm", "aterm", "rxvt",
                "screen", "kterm", "rxvt-unicode", "cygwin"]

        self._setup_color()

    def ctext(self, txt='', fg='fg_default', bg='bg_default', *attr):
        if not self.is_term:
            self.nctext(txt)
            return

        tmp = self.__esc + self.__seq[fg] + ';' + self.__seq[bg]
        for x in attr:
            tmp += ';' + self.__seq[x]
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
        print >> sys.stderr, \
            "Couldn't find the ctypes module. Sorry, no color."

class _Win32Term(_TerminalBase):
    def __init__(self):
        super(_Win32Term, self).__init__()

        # See the M$ website (or MSDN) for info. on these values.
        STDIN_HANDLE = -10
        STDOUT_HANDLE = -11
        STDERR_HANDLE = -12
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
                and globals().has_key('ctypes'))

        self.__seq = {}
        self.__seq["normal"]       = 0
        self.__seq["bold"]         = FG_I
        self.__seq["faint"]        = 0
        self.__seq["standout"]     = 0
        self.__seq["underline"]    = 0
        self.__seq["blink"]        = 0
        self.__seq["reverse"]      = 0
        self.__seq["fg_bold"]      = FG_I
        self.__seq["fg_black"]     = 0
        self.__seq["fg_red"]       = FG_R
        self.__seq["fg_green"]     = FG_G
        self.__seq["fg_yellow"]    = FG_R | FG_G
        self.__seq["fg_blue"]      = FG_B
        self.__seq["fg_magenta"]   = FG_R | FG_B
        self.__seq["fg_cyan"]      = FG_G | FG_B
        self.__seq["fg_white"]     = FG_R | FG_G | FG_B
        self.__seq["fg_default"]   = 0
        self.__seq["bg_bold"]      = BG_I
        self.__seq["bg_black"]     = 0
        self.__seq["bg_red"]       = BG_R
        self.__seq["bg_green"]     = BG_G
        self.__seq["bg_yellow"]    = BG_R | BG_G
        self.__seq["bg_blue"]      = BG_B
        self.__seq["bg_magenta"]   = BG_R | BG_B
        self.__seq["bg_cyan"]      = BG_G | BG_B
        self.__seq["bg_white"]     = BG_R | BG_G | BG_B
        self.__seq["bg_default"]   = 0
        self.__seq["default"]      = 0x07

        if self.is_term:
            self.soh = ctypes.windll.kernel32.GetStdHandle(STDOUT_HANDLE)

            csbi = CONSOLE_SCREEN_BUFFER_INFO()
            ctypes.windll.kernel32.GetConsoleScreenBufferInfo(
                self.soh, ctypes.byref(csbi))
            self.__seq["default"] = csbi.wAttributes
            self.__seq["fg_default"] = csbi.wAttributes & FG_M
            self.__seq["bg_default"] = csbi.wAttributes & BG_M

        self._setup_color()

    def ctext(self, txt='', fg='fg_default', bg='bg_default', *attr):
        if not self.is_term:
            self.nctext(txt)
            return

        c = self.__seq[fg] | self.__seq[bg]
        for x in attr:
            c |= self.__seq[x]

        dc = self.__seq['default']

        ctypes.windll.kernel32.SetConsoleTextAttribute(self.soh, c)
        self.so.write(txt)
        ctypes.windll.kernel32.SetConsoleTextAttribute(self.soh, dc)

    def title(self, title):
        if not self.is_term: return

        t = ctypes.c_char_p(title)
        ctypes.windll.kernel32.SetConsoleTitleA(t)

    def clear_and_home(self):
        if not self.is_term: return

        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        ctypes.windll.kernel32.GetConsoleScreenBufferInfo(self.soh,
            ctypes.byref(csbi))

        con_size = ctypes.wintypes.DWORD(csbi.dwSize.X * csbi.dwSize.Y)

        homepos = ctypes.wintypes.COORD(0, 0)
        chars_written = ctypes.wintypes.DWORD(0)

        ctypes.windll.kernel32.FillConsoleOutputCharacterA(self.soh,
            ctypes.c_char(' '), con_size, homepos,
            ctypes.byref(chars_written))

        # Use current attributes here or the ones we started with?
        ctypes.windll.kernel32.FillConsoleOutputAttribute(self.soh,
            csbi.wAttributes, con_size, homepos,
            ctypes.byref(chars_written))

        ctypes.windll.kernel32.SetConsoleCursorPosition(self.soh,
            homepos)

    def rows_and_cols(self):
        if not self.is_term: return self.default_R_and_C

        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        ctypes.windll.kernel32.GetConsoleScreenBufferInfo(self.soh,
            ctypes.byref(csbi))

        R = csbi.srWindow.Bottom - csbi.srWindow.Top + 1
        C = csbi.srWindow.Right - csbi.srWindow.Left + 1

        return R, C

# _ANSITerm explicitly only supports os.name == 'posix'.  But, if it's not, it
# will only be slightly lame and not dead.
Terminal = _Win32Term if os.name == 'nt' else _ANSITerm
