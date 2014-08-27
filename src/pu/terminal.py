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
        self._seq = {}

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
        self.ctext('Orbis, te saluto! ==>', 'fg_blue', 'bg_green', 'bold')
        self.ctext(' Hello, world!\n', 'fg_green', 'bg_blue', 'bold')
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
        self.ctext('white on red\n', 'fg_white', 'bg_red')
        self.ctext('black on red\n', 'fg_black', 'bg_red')
        self.ctext('black on green\n', 'fg_black', 'bg_green')
        self.ctext('black on yellow\n', 'fg_black', 'bg_yellow')
        self.ctext('white on blue\n', 'fg_white', 'bg_blue')
        self.ctext('black on magenta\n', 'fg_black', 'bg_magenta')
        self.ctext('black on cyan\n', 'fg_black', 'bg_cyan')
        self.ctext('black on white\n', 'fg_black', 'bg_white')
        self.ctext('bold black on white\n', 'fg_black', 'bg_white', 'bold')
        self.title('terminal.py was here...')

class _ANSITerm(_TerminalBase):
    ESC = '\x1b['
    def __init__(self):
        super(_ANSITerm, self).__init__()

        self.is_term = ('posix' == os.name and self.so.isatty())

        self.__esc = "\x1b["

        seq = self._seq
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

        seq = self._seq
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

    @staticmethod
    def term_colors():
        """Return the 256 terminal colors as a list of RGB hex triples."""
        _rgbfmt = ('{:02x}' * 3)

        def _3(x, on):
            _ = lambda i: on if i else 0
            n = divmod(x, 8)[1]
            return _rgbfmt.format(_(n & 0b1), _(n & 0b10), _(n & 0b100))

        rgb = []
        ra = rgb.append

        # system colors
        for i in xrange(7): ra(_3(i, 0x80))
        ra(_3(7, 0xc0))
        ra(_3(7, 0x80))
        for i in xrange(9, 16): ra(_3(i, 0xff))

        # color cube
        for r in xrange(6):
            for g in xrange(6):
                for b in xrange(6):
                    i = 36 * r + 6 * g + b + 16
                    ra(_rgbfmt.format(
                        r and (r * 40 + 55),
                        g and (g * 40 + 55),
                        b and (b * 40 + 55)))

        # grayscale ramp
        for i in xrange(24):
            x = (i * 10) + 8
            ra(_rgbfmt.format(x, x, x))

        return rgb

    @staticmethod
    def print_term_colors(only = None):
        """Print the terminal colors to standard out.

        If desired, the output can be limited by setting `only` to a string
        combination of ``system``, ``color-cube`` or ``gray-ramp`` separated by
        whitespace; e.g., `only` = ``system gray-ramp`` will produce just the
        system colors and the gray-scale ramp.
        """
        only = only.split() if only else 'system color-cube gray-ramp'.split()
        RGB = _ANSITerm.term_colors()
        ESC = _ANSITerm.ESC
        RESET = ESC + '0m'
        fg = ESC + '38;5;{0}m {0:03d}#{1}'

        def reset():
            print(RESET, end = '')

        def pfmt(i):
            print(fg.format(i, RGB[i]), sep = '', end = '')

        if 'system' in only:
            print('System colors:')
            for i in xrange(16):
                pfmt(i)
                if 3 == divmod(i, 4)[1]: print()
            reset()

        if 'color-cube' in only:
            print('Color cube (6x6x6):')
            for i in xrange(16, 232):
                pfmt(i)
                if 3 == divmod(i, 6)[1]: print()
            reset()

        if 'gray-ramp' in only:
            print('Gray-scale ramp:')
            for i in xrange(232, 256):
                pfmt(i)
                if 3 == divmod(i, 6)[1]: print()
            reset()

if 'nt' == os.name:
    try:
        import ctypes
        import ctypes.wintypes
    except ImportError:
        print("Couldn't find the ctypes module. Sorry, no color.",
            file = sys.stderr)
    else:
        # Don't clobber ctypes.wintypes but make the function setup below
        # easier.
        class _wintypes(object):
            def __getattr__(self, name):
                return getattr(ctypes.wintypes, name)

        def check_BOOL(result, func, args):
            if not result:
                raise ctypes.WinError()

            return result

        def check_HANDLE(result, func, args):
            if not result:
                raise RuntimeError('No standard handle available.')

            # INVALID_HANDLE_VALUE = -1
            if -1 == result:
                raise ctypes.WinError()

            return result

        def check_DWORD(result, func, args):
            if 'GetModuleFileNameA' == func.__name__:
                if (0 == result) or (len(args[-2]) == result):
                    raise ctypes.WinError()

            return result

        wintypes = _wintypes()
        wintypes._checks = dict(
            BOOL = check_BOOL, HANDLE = check_HANDLE, DWORD = check_DWORD)
        wintypes.COORD = wintypes._COORD

        class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
            _fields_ = [
                ('dwSize', wintypes.COORD),
                ('dwCursorPosition', wintypes.COORD),
                ('wAttributes', wintypes.WORD),
                ('srWindow', wintypes.SMALL_RECT),
                ('dwMaximumWindowSize', wintypes.COORD)
                ]
        # Out of paranoia, make sure the handle to the DLL doesn't get garbage
        # collected.
        wintypes._kernel32 = k32 = ctypes.WinDLL('kernel32')
        wintypes.CHAR = ctypes.c_char
        wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)
        wintypes.PCONSOLE_SCREEN_BUFFER_INFO = ctypes.POINTER(
            CONSOLE_SCREEN_BUFFER_INFO)
        L = locals()
        for line in '''
                FillConsoleOutputAttribute:BOOL:HANDLE,WORD,DWORD,COORD,LPDWORD
                FillConsoleOutputCharacterA:BOOL:HANDLE,CHAR,DWORD,COORD,LPDWORD
                GetConsoleScreenBufferInfo:BOOL:HANDLE,PCONSOLE_SCREEN_BUFFER_INFO
                GetModuleFileNameA:DWORD:HMODULE,LPSTR,DWORD
                GetStdHandle:HANDLE:DWORD
                SetConsoleCursorPosition:BOOL:HANDLE,COORD
                SetConsoleTextAttribute:BOOL:HANDLE,WORD
                SetConsoleTitleA:BOOL:LPCSTR
                '''.split():
            name, res, args = line.split(':')
            L[name] = func = getattr(k32, name)
            func.restype = getattr(wintypes, res)
            func.argtypes = [getattr(wintypes, i) for i in args.split(',')]
            func.errcheck = wintypes._checks[res]
        del k32, L, line, name, res, args, func, i

        def _kernel32_path(limit = 0x100):
            buf = ctypes.create_string_buffer(limit)
            lim = wintypes.DWORD(limit)
            GetModuleFileNameA(wintypes._kernel32._handle, buf, lim)

            return buf.value

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
                and 'ctypes' in globals())

        seq = self._seq
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
            self.soh = soh = GetStdHandle(STDOUT_HANDLE)

            csbi = CONSOLE_SCREEN_BUFFER_INFO()
            GetConsoleScreenBufferInfo(soh, csbi)
            seq["default"] = csbi.wAttributes
            seq["fg_default"] = csbi.wAttributes & FG_M
            seq["bg_default"] = csbi.wAttributes & BG_M

        self._setup_color()

    def __del__(self):
        SetConsoleTextAttribute(self.soh, self._seq['default'])
        super(_Win32Term, self).__del__()

    def ctext(self, txt='', fg='fg_default', bg='bg_default', *attr):
        if not self.is_term:
            self.nctext(txt)
            return

        soh, seq = self.soh, self._seq

        c = seq[fg] | seq[bg]
        for x in attr: c |= seq[x]

        SetConsoleTextAttribute(soh, c)
        self.so.write(txt)
        SetConsoleTextAttribute(soh, seq['default'])

    def title(self, title):
        if not self.is_term: return

        SetConsoleTitleA(ctypes.c_char_p(title))

    def clear_and_home(self):
        if not self.is_term: return

        soh = self.soh

        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        GetConsoleScreenBufferInfo(soh, csbi)

        con_size = wintypes.DWORD(csbi.dwSize.X * csbi.dwSize.Y)

        homepos = wintypes.COORD(0, 0)
        chars_written = wintypes.DWORD(0)

        FillConsoleOutputCharacterA(soh, ctypes.c_char(' '), con_size,
            homepos, chars_written)
        if con_size.value != chars_written.value:
            raise RuntimeError('Blanks underwritten: {} != {}'.format(
                con_size.value, chars_written.value))

        FillConsoleOutputAttribute(soh, csbi.wAttributes, con_size, homepos,
            chars_written)
        if con_size.value != chars_written.value:
            raise RuntimeError('Attributes underwritten: {} != {}'.format(
                con_size.value, chars_written.value))

        SetConsoleCursorPosition(soh, homepos)

    def rows_and_cols(self):
        if not self.is_term: return self.default_R_and_C

        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        GetConsoleScreenBufferInfo(self.soh, csbi)

        R = csbi.srWindow.Bottom - csbi.srWindow.Top + 1
        C = csbi.srWindow.Right - csbi.srWindow.Left + 1

        return R, C

# _ANSITerm explicitly only supports os.name == 'posix'.  But, if it's not, it
# will only be slightly lame and not dead.
Terminal = _Win32Term if os.name == 'nt' else _ANSITerm
