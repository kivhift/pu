#
# Copyright (c) 2013 Joshua Hughes <kivhift@gmail.com>
#
import re

from pu.utils import is_an_integer, is_a_string

class Enumeration(object):
    """C's enum type in Python.

    Inspired by PC2e:{6.2, 16.9}.

    """
    class ConstError(Exception): pass

    def __init__(self,
            name = 'enum', enumees = (), unique = True, freeze = False):
        """Enumerate the values as given in `enumees`.

        The strings in `enumees` determine, at the bare minimum, the initial
        attributes used to hold the enumerated values.  The values can be
        either implicitly or explicitly given along with a description of the
        value.  Each string in `enumees` should have the following format::

            <name>[= <int>][= <description>]

        If <int> is given, then it is used for <name>'s value.  Otherwise, the
        next value is used.  Similarly, if <description> is given, then it is
        used for <name>'s description.  Otherwise, <name> has no description.

        `unique` specifies whether or not the values should be unique.  If
        `freeze` is True, then adding new values is disallowed.

        If the enumeration isn't frozen, then new values can be added after
        instantiation.  The post-instantiation syntax is similar to the one
        used for `enumees`.  New values are added as given below::

            >>> e = Enumeration('eg')
            >>> e.a           # Implicit value, autovivify.
            >>> e.b = 2       # Explicit value.
            >>> e.c = "C"     # Implicit value, explicit description.
            >>> e.d = 10, "D" # Explicit value, explicit description.
            >>> for c in 'abcd': print getattr(e, c),
            0 2 3 10

        """
        super(Enumeration, self).__init__()

        enumee_re = re.compile(
            r'''^(?P<enumee>\w+)
                (
                    (\s*=\s*(?P<intval>\d+))?
                    (\s*=\s*(?P<desc>.*))?
                )?$
            ''', re.X)

        sa = super(Enumeration, self).__setattr__
        sa('_super_setattr', sa)
        sa('name', name)
        sa('_names', set())
        sa('_next_val', 0)
        sa('_descriptions', {})
        sa('_values', set())
        sa('unique', unique)
        sa('frozen', False)

        for e in enumees:
            m = enumee_re.match(e)
            if m is None: raise ValueError('Invalid enumee: %r' % e)
            nm, iv, d = m.group('enumee'), m.group('intval'), m.group('desc')
            self.__setattr__(nm, (int(iv) if iv else self._next_val, d))

        sa('frozen', freeze)

    def __setattr__(self, name, value):
        if self.frozen: raise Enumeration.ConstError('Enumeration is frozen.')

        sd = self.__dict__
        if name in sd: raise Enumeration.ConstError('Cannot rebind %s.' % name)

        i, desc = self._next_val, None
        if is_a_string(value):
            desc = value
        elif is_an_integer(value):
            i = value
        else:
            i, desc = value

        if self.unique and i in self._values:
            raise ValueError('Value already used: %d.' % i)

        sa = self._super_setattr
        sa(name, i)
        self._names.add(name)
        self._values.add(i)
        sa('_next_val', i + 1)
        if desc:
            sdd = self._descriptions
            sdd[name] = desc
            sdd[i] = desc

    def __delattr__(self, name):
        if name in self.__dict__:
            raise Enumeration.ConstError('Cannot delete %s.' % name)
        raise AttributeError(name)

    def __getattr__(self, name):
        self.__setattr__(name, self._next_val)
        return self.__getattribute__(name)

    def freeze(self):
        """Freeze the enumeration to disallow changes."""
        self._super_setattr('frozen', True)

    @property
    def names(self):
        """The enumee names."""
        return sorted(list(self._names))

    @property
    def values(self):
        """The current values of the enumeration."""
        return list(self._values)

    def description(self, enumee):
        """Return the description for `enumee`.

        `enumee` can be either the value or name of the desired attribute.  If
        no description is available, None is returned.  If the enumeration
        isn't unique, then using an integer value isn't recommended since
        previous descriptions, if given, will be clobbered if multiple
        identical values are set.

        KeyError is raised if `enumee` isn't set.
        """
        if (enumee in self._values) or (enumee in self.__dict__):
            return self._descriptions.get(enumee)
        raise  KeyError(enumee)
