#
# Copyright (c) 2013 Joshua Hughes <kivhift@gmail.com>
#
import sys

class Tag(object):
    _name = ''
    def __init__(self, *a, **kw):
        super(Tag, self).__init__()
        self.content = list(a)
        self.attributes = kw

    def __str__(self):
        name = self._name
        content = ''.join(str(c) for c in self.content)
        atts = ''.join(
            ' {}="{}"'.format(k, v) for k, v in self.attributes.iteritems())
        if content:
            return '<{0}{1}>{2}</{0}>'.format(name, atts, content)
        else:
            return '<{0}{1}/>'.format(name, atts)

    def add(self, *content):
        self.content.extend(content)
        if 1 == len(content):
            return content[0]
        else:
            return content

    @staticmethod
    def factory(name):
        class NT(Tag): _name = name
        NT.__name__ = name.replace('-', '_').replace('.', '_')
        return NT.__name__, NT

    @staticmethod
    def vivify(tags, into = None):
        if into is None:
            into = sys.modules[__name__]
        for tag in tags:
            setattr(into, *Tag.factory(tag))
