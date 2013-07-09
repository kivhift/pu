#
# Copyright (c) 2012-2013 Joshua Hughes <kivhift@gmail.com>
#
import re

from pu.utils import is_a_string, is_an_integer, DataContainer

class SelfSerializerError(Exception): pass
class SelfSerializerEmptyHeaderError(Exception): pass

class SelfSerializer(object):
    '''
    SelfSerializer can serialize itself given that every item in its __dict__
    is serializable.  Only the types in SelfSerializer._serializable_types are
    considered serializable.

    The interface should be famililar to anyone that has used the pickle or
    json modules except that the instance itself has .dump() and .load()
    instead of the library code.
    '''

    _record_sep = '\x1eSS'
    _serializable_types = (int, long, str, list, dict, float)

    def __init__(self):
        super(SelfSerializer, self).__init__()

    def dump(self, fout, append = True):
        '''
        Dump the calling instance to fout.  fout can either be a file to open
        or a file-like object to be written to.  A to-be-opened file is
        appended to by default.  Make append false to truncate a
        possibly-extant file.
        '''
        if not self._is_serializable():
            raise SelfSerializerError('Cannot serialize.')

        d = self.__dict__
        keys = d.keys()
        keys.sort()

        f = open(fout, 'ab' if append else 'wb') if is_a_string(fout) else fout
        f.write('%s %s %d\n' % (
            SelfSerializer._record_sep, self.__class__.__name__, len(keys)))
        for k in keys:
            self._serialize(f, k, d[k])
        if is_a_string(fout): f.close()

    def load(self, fin):
        '''
        Load the calling instance from fin.  fin can either be a file to open
        or a file-like object to be read from.
        '''
        f = open(fin, 'rb') if is_a_string(fin) else fin
        ln = f.readline()
        if not ln: raise SelfSerializerEmptyHeaderError('Empty header.')
        H = ln.split()
        if (len(H) != 3) or (H[0] != SelfSerializer._record_sep):
            raise SelfSerializerError('Incorrect record separator.')
        class_name, indicated_len = H[1], int(H[2])
        if self.__class__.__name__ != class_name:
            raise SelfSerializerError('Incorrect name: %s' % class_name)
        if indicated_len < 0:
            raise SelfSerializerError('Invalid length: %d' % indicated_len)
        tmp_dict = dict()
        for i in xrange(indicated_len):
            name, val = self._deserialize(f)
            tmp_dict[name] = val
        if len(tmp_dict) != indicated_len:
            raise SelfSerializerError(
                'Incorrect number of items: %d != %d' % (
                    len(tmp_dict), indicated_len))
        if is_a_string(fin): f.close()

        self.__dict__ = tmp_dict

    def _is_serializable(self):
        for v in self.__dict__.itervalues():
            if not isinstance(v, SelfSerializer._serializable_types):
                return False
        return True

    def _serialize(self, f, name, val):
        if is_an_integer(val):
            f.write('^i %s %d\n' % (name, val))
        elif isinstance(val, str):
            f.write('^b %s %d\n' % (name, len(val)))
            f.write(val)
        elif isinstance(val, list):
            f.write('^a %s %d\n' % (name, len(val)))
            for i, e in enumerate(val):
                self._serialize(f, str(i), e)
        elif isinstance(val, dict):
            f.write('^h %s %d\n' % (name, len(val)))
            keys = val.keys()
            keys.sort()
            for i, k in enumerate(keys):
                ks = str(i)
                self._serialize(f, ks, k)
                self._serialize(f, ks, val[k])
        elif isinstance(val, float):
            hexflt = val.hex()
            f.write('^f %s %d\n' % (name, len(hexflt)))
            f.write(hexflt)
        else:
            raise ValueError("Can't serialize %s, %s." % (name, type(val)))

    _type_re = re.compile(
        '^\^(?P<type_>[ibahf])\s+(?P<name>\w+)\s+(?P<intval>-?\d+)$')
    def _deserialize(self, f):
        L = f.readline()
        M = SelfSerializer._type_re.match(L)
        if M is None:
            raise SelfSerializerError('Had trouble determining type.')
        type_ = M.group('type_')
        name = M.group('name')
        intval = int(M.group('intval'))
        if 'i' == type_:
            return name, intval
        elif 'b' == type_:
            return name, f.read(intval)
        elif 'a' == type_:
            tmp = list()
            for i in xrange(intval):
                n, v = self._deserialize(f)
                if n != str(i):
                    raise SelfSerializerError(
                        'Array element out of order.')
                tmp.append(v)
            return name, tmp
        elif 'h' == type_:
            tmp = dict()
            for i in xrange(intval):
                si = str(i)
                n, k = self._deserialize(f)
                if n != si:
                    raise SelfSerializerError('dict key out of order.')
                n, v = self._deserialize(f)
                if n != si:
                    raise SelfSerializerError('dict value out of order.')
                tmp[k] = v
            return name, tmp
        elif 'f' == type_:
            return name, float.fromhex(f.read(intval))

class SelfSerializingDataContainer(DataContainer, SelfSerializer):
    def __init__(self, *args, **kwargs):
        super(SelfSerializingDataContainer, self).__init__(*args, **kwargs)
