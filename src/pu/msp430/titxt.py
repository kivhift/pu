#
# Copyright (c) 2013 Joshua Hughes <kivhift@gmail.com>
#
import array
import cStringIO
import re

from pu.utils import is_an_integer

class Section(object):
    def __init__(self, addr, buffer):
        self.start_addr = addr
        self.buffer = buffer
        self.end_addr = addr + len(buffer) - 1

    def __add__(self, other):
        if self.end_addr + 1 != other.start_addr:
            raise ValueError('Sections are not adjacent!')

        return self.__class__(self.start_addr, self.buffer + other.buffer)

    def __cmp__(self, other):
        ssa = self.start_addr
        osa = other.start_addr
        if ssa < osa:
            return -1
        elif ssa > osa:
            return 1
        else:
            return 0

    def __len__(self):
        return len(self.buffer)

    def __str__(self):
        ret = cStringIO.StringIO()
        ret.write('@{:04x}\n'.format(self.start_addr))
        i = 0
        for b in self.buffer:
            ret.write('{}{:02x}'.format(' ' if i else '', b))
            i += 1
            if 16 == i:
                i = 0
                ret.write('\n')
        if i:
            ret.write('\n')
        return ret.getvalue()

class FirmwareImage(object):
    def __init__(self, infile = None):
        self.section = []

        if infile: self.parse(infile)

    def __str__(self):
        ret = cStringIO.StringIO()
        for sec in self.section:
            ret.write(str(sec))
        ret.write('q\n')

        return ret.getvalue()

    def __getitem__(self, key):
        if is_an_integer(key):
            for sec in self.section:
                if key >= sec.start_addr and key <= sec.end_addr:
                    key -= sec.start_addr
                    return sec.buffer[key]
        else:
            start = key.start
            if start is None:
                raise IndexError('Must give start index.')
            stop = key.stop
            for sec in self.section:
                if start >= sec.start_addr and start <= sec.end_addr:
                    start -= sec.start_addr
                    if stop is not None:
                        stop -= sec.start_addr
                    return sec.buffer[slice(start, stop, key.step)]

        raise IndexError('Given index is invalid.')

    def merge_sections(self):
        self.section.sort()
        sec = self.section
        i = 0
        while i < (len(sec) - 1):
            if sec[i].end_addr + 1 == sec[i + 1].start_addr:
                sec[i] += sec.pop(i + 1)
                continue
            i += 1

    def parse(self, infile):
        quit_re = re.compile('^[qQ]$')
        addr_re = re.compile('^@[0-9a-fA-F]{4}$')
        bytes_re = re.compile('^[0-9a-fA-F]{2}(\s+[0-9a-fA-F]{2}){15}$')
        section = []
        addr = None
        buf = None
        def _add_sec():
            if buf is not None:
                section.append(Section(addr, buf))

        with open(infile, 'rb') as inf:
            for i, line in enumerate(inf):
                ln = line.strip()
                if quit_re.match(ln):
                    _add_sec()
                    break
                elif addr_re.match(ln):
                    _add_sec()
                    addr = int(ln[1:], 16)
                    buf = array.array('B')
                elif bytes_re.match(ln):
                    buf.extend([int(x, 16) for x in ln.split()])
                else:
                    raise ValueError('Invalid line @ %d: %r' % (i, line))
            if not quit_re.match(ln):
                raise ValueError('Ran out of file without finding "q".')

        self.section = section
