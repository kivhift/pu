#!/usr/bin/python

import os

class LineListIO(object):
    def __init__(self, linelist = []):
        self.setLineList(linelist)

    def setLineList(self, linelist):
        self._lines = linelist
        self._ln = 0
        self._intralnpos = 0
        self._pos = 0

    def __size(self):
        sz = 0
        for ln in self._lines:
            sz += len(ln) + 1

        return sz

    def read(self, n = None):
        if n is not None:
            to_go = n
        else:
            to_go = self.__size() - self._pos

        if 0 == to_go: return ''

        buf = ''
        while self._ln < len(self._lines):
            delta = len(self._lines[self._ln]) - self._intralnpos
            if to_go < delta: delta = to_go
            if self._intralnpos < len(self._lines[self._ln]):
                buf += self._lines[self._ln][
                    self._intralnpos : self._intralnpos + delta]
                self._intralnpos += delta
                to_go -= delta
            if to_go > 0 and self._intralnpos == len(self._lines[self._ln]):
                buf += '\n'
                to_go -= 1
                self._ln += 1
                self._intralnpos = 0
            if 0 == to_go: break

        self._pos += len(buf)

        return buf

    def tell(self):
        return self._pos

    def seek(self, offset, whence = os.SEEK_SET):
        if os.SEEK_SET == whence:
            if 0 != offset:
                raise NotImplementedError('Can only seek to start of file.')
            self._ln = self._pos = 0
        elif os.SEEK_END == whence:
            if 0 != offset:
                raise NotImplementedError('Can only seek to end of file.')
            self._ln = len(self._lines)
            self._pos = self.__size()
        else:
            raise ValueError('Invalid whence.')

        self._intralnpos = 0
