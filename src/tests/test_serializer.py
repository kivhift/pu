#
# Copyright (c) 2012 Joshua Hughes <kivhift@gmail.com>
#
from nose.tools import assert_raises

import os
import StringIO
import tempfile

import pu.serializer

_data_dir = 'data'
def _path(name):
    return os.path.join(_data_dir, name)

class EqHelper(pu.serializer.SelfSerializer):
    def __eq__(self, other):
        if set(self.__dict__) != set(other.__dict__):
            return False

        for k, v in self.__dict__.iteritems():
            if other.__dict__[k] != v:
                return False
            if type(other.__dict__[k]) != type(v):
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

def test_serializability():
    s = EqHelper()
    # ints
    s.a = 0
    s.b = 0x2ff
    s.c = -77
    s.d = 1<<163
    s.e = -1 * s.d
    # float
    s.f = 0.0
    s.g = 3.14159
    s.h = -1.0 * s.g
    # str
    s.i = ''
    s.j = '\0\x01\x02\x03hi'
    s.k = '\x0f.\xf7D\x8buL2\xce\xc2p\x95\xfa'
    # list
    s.l = []
    s.m = [''] * 4
    s.n = [[]] * 3
    s.o = list('abcd')
    s.p = [{}]
    # dict
    s.q = {}
    s.r = {0 : '0', 'a' : 1, 'b' : 2, 'c' : {}, 'd' : []}

    f = tempfile.TemporaryFile()
    s.dump(f)
    s.dump(f)
    f.seek(0)
    s0, s1 = EqHelper(), EqHelper()
    s0.load(f)
    s1.load(f)

    assert s == s0
    assert s == s1
    assert s0 == s1

def test_append():
    s = EqHelper()
    s.eg = '\x00this is some text...'
    s.ex = 1234

    fout = tempfile.NamedTemporaryFile(delete = False)
    fout.close()
    s.dump(fout.name)
    s.dump(fout.name)

    s0, s1 = EqHelper(), EqHelper()
    s0.load(fout.name)
    with open(fout.name, 'rb') as f:
        s1.load(f)
        s1.load(f)

    os.remove(fout.name)

    assert s == s0
    assert s == s1
    assert s0 == s1

def test_exceptions():
    s = EqHelper()
    s.s = EqHelper()
    with assert_raises(pu.serializer.SelfSerializerError):
        s.dump(tempfile.TemporaryFile())
    with assert_raises(pu.serializer.SelfSerializerError):
        s.load(_path('bad-item-count'))
    with assert_raises(pu.serializer.SelfSerializerError):
        s.load(_path('bad-length'))
    with assert_raises(pu.serializer.SelfSerializerError):
        s.load(_path('bad-name'))
    with assert_raises(pu.serializer.SelfSerializerError):
        s.load(_path('bad-record-sep'))

def test_load():
    s, s0 = EqHelper(), EqHelper()
    s0.eg_flt = 0.0
    s0.eg_int = -1
    s0.eg_str = 'This is some text.'
    s.load(_path('good'))
    assert s0 == s

def test_interaction_with_file_likes():
    s, s0 = EqHelper(), EqHelper()
    buf = StringIO.StringIO()
    s.some_text = 'Will this work?'
    s.an_integer = 0
    s.dump(buf)
    buf.seek(0)
    s0.load(buf)

    assert s == s0
