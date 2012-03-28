from nose.tools import assert_raises

import pu.utils

def test_DataContainer__init__():
    pud = pu.utils.DataContainer
    d = pud()
    assert 0 == len(d)
    def chk(it):
        assert 2 == len(it)
        assert 0 == it.a
        assert 1 == it.b
    chk(pud(a = 0, b = 1))
    chk(pud({'a' : 0, 'b' : 1}))
    chk(pud({'a' : 0}, b = 1))
    with assert_raises(TypeError): d = pud({'a' : 0}, {'b' : 1})

def test_DataContainer__repr__():
    pud = pu.utils.DataContainer
    assert 'DataContainer()' == repr(pud())
    assert 'DataContainer(a = 1)' == repr(pud(a = 1))
    assert 'DataContainer(a = 1, b = 2)' == repr(pud(b=2,a=1))
    assert "DataContainer({'0' : 0})" == repr(pud({'0':0}))
    assert "DataContainer({'0' : 0, '9' : '9'}, a = 1, b = 2)" == repr(pud(
        {'9':'9','0':0},b=2,a=1))

class TestDataContainer(object):
    def __init__(self):
        self.d = pu.utils.DataContainer()

    def test___contains__(self):
        d = self.d
        assert 'a' not in d
        d.a = 0
        assert 'a' in d

    def test___len__(self):
        d = self.d
        assert 0 == len(d)
        d.a = 0
        assert 1 == len(d)
        d.a = 1
        assert 1 == len(d)
        d.b = 2
        assert 2 == len(d)
        d.c = 3
        assert 3 == len(d)

    def test___getitem__(self):
        d = self.d
        with assert_raises(TypeError): d[{}]
        with assert_raises(AttributeError): d['a']
        d.a = '.'
        assert d.a == d['a']
        assert id(d.a) == id(d['a'])

    def test___setitem__(self):
        d = self.d
        with assert_raises(TypeError): d[{}] = 0
        a = '.'
        d['a'] = a
        assert a == d['a']
        assert id(a) == id(d['a'])

    def test___delitem__(self):
        d = self.d
        with assert_raises(TypeError): del d[{}]
        with assert_raises(AttributeError): del d['a']
        d['a'] = '.'
        del d['a']
        with assert_raises(AttributeError): d['a']

    def setup_attrs(self):
        d = self.d
        s = set('abc')
        for e in s: setattr(d, e, e)
        return d, s

    def test___iter__(self):
        for k in self.d: raise UserWarning('Should not happen.')
        d, s = self.setup_attrs()
        for k in d: s.remove(k)
        assert 0 == len(s)

    def test_keys(self):
        d, s = self.setup_attrs()
        for k in d.keys(): s.remove(k)
        assert 0 == len(s)

    def test_values(self):
        d, s = self.setup_attrs()
        for v in d.values():
            assert id(v) == id(getattr(d, v))
            s.remove(v)
        assert 0 == len(s)

    def test_items(self):
        d, s = self.setup_attrs()
        for k, v in d.items():
            assert id(v) == id(getattr(d, k))
            s.remove(k)
        assert 0 == len(s)

    def test_get(self):
        d = self.d
        assert d.get('a') is None
        assert 0 == d.get('a', 0)
        assert 'a' == d.get(0, 'a')
        with assert_raises(TypeError): d.get({})
        d.a = 0
        assert id(d.a) == id(d.get('a'))
        del d.a
        assert d.get('a') is None

    def test_clear(self):
        d, s = self.setup_attrs()
        assert 3 == len(d)
        d.clear()
        assert 0 == len(d)

    def test_setdefault(self):
        d = self.d
        _, a = '_', 'a'
        assert d.setdefault(_) is None
        assert d._ is None
        assert d.setdefault(_, a) is None
        assert id(a) == id(d.setdefault(a, a))
        assert id(a) == id(d.setdefault(a))
        assert id(a) == id(d.a)
        with assert_raises(TypeError): d.setdefault({})

    def test_iterkeys(self):
        d, s = self.setup_attrs()
        for k in d.iterkeys(): s.remove(k)
        assert 0 == len(s)

    def test_itervalues(self):
        d, s = self.setup_attrs()
        for v in d.itervalues():
            assert id(v) == id(getattr(d, v))
            s.remove(v)
        assert 0 == len(s)

    def test_iteritems(self):
        d, s = self.setup_attrs()
        for k, v in d.iteritems():
            assert id(v) == id(getattr(d, k))
            s.remove(k)
        assert 0 == len(s)

    def test_copy(self):
        d, _ = self.setup_attrs()
        cp = d.copy()
        sd = set(d)
        scp = set(cp)
        assert sd == scp
        for k in d:
            assert id(d[k]) == id(cp[k])

    def test_update(self):
        d = self.d
        with assert_raises(TypeError): d.update({'a' : 0}, {'b' : 1})
        with assert_raises(TypeError): d.update({0 : 'a'})
        d.update({'a' : 0}, b = 1, c = 2)
        assert 3 == len(d)
        assert 0 == d.a
        assert 1 == d.b
        assert 2 == d.c
        d.update([('a', 3), ('b', 4), ('c', 5)])
        assert 3 == len(d)
        assert 3 == d.a
        assert 4 == d.b
        assert 5 == d.c
        d.update()
        assert 3 == len(d)
        d.update({})
        assert 3 == len(d)
        d.update(d = 6)
        assert 4 == len(d)
        assert 3 == d.a
        assert 4 == d.b
        assert 5 == d.c
        assert 6 == d.d
