#!/usr/bin/python
#
# Copyright (c) 2010-2012 Joshua Hughes <kivhift@gmail.com>
#
import os
import tempfile

import PyQt4
from PyQt4.uic import compileUi

pyqt4_path = PyQt4.__path__[0]
def _tool_path(t):
    return os.path.join(pyqt4_path, t)

lrelease_tool = _tool_path('lrelease')
pylupdate4_tool = _tool_path('pylupdate4')
pyrcc4_tool = _tool_path('pyrcc4')

def pyui_name(ui):
    '''
    Generate the python-module name from the Qt UI file.
    '''
    h, t = os.path.split(ui)
    return os.path.join(h, 'ui_' + t.replace('.ui', '.py'))

def pyqrc_name(qrc):
    '''
    Generate the python-module name from the Qt QRC file.
    '''
    h, t = os.path.split(qrc)
    t = t.replace('.qrc', '.py')
    t = t.replace('-', '_')
    return os.path.join(h, 'qrc_' + t)

def generate_pyui(target, source, env):
    '''
    Generate a Python module for the given Qt UI file.
    '''
    with open(str(target[0]), 'wb') as f:
        compileUi(str(source[0]), f, execute = True, indent = 4)

def setup_pyqt4_builders(env, builder_factory):
    env['BUILDERS']['PyUic4'] = builder_factory(action = generate_pyui)
    env['BUILDERS']['PyRcc4'] = builder_factory(
        action = pyrcc4_tool + ' -py2 -o $TARGET $SOURCE')
    env['BUILDERS']['PyLupdate4'] = builder_factory(
        action = pylupdate4_tool + ' -noobsolete -verbose $SOURCES -ts $TARGET')
    env['BUILDERS']['Lrelease'] = builder_factory(action = lrelease_tool
        + ' -compress -nounfinished $SOURCES -qm $TARGET')

def pyuic4(env, ui):
    '''
    Carefully generate the Python module for the given Qt UI file.
    '''
    t = env.Precious(env.NoClean(env.PyUic4(
        target = pyui_name(ui), source = ui)))
    env.Depends(t, ui)

    return t

def pyrcc4(env, qrc, depends = []):
    '''
    Carefully generate the resource module from the given QRC file with the
    given dependencies.
    '''
    t = env.Precious(env.NoClean(env.PyRcc4(
        target = pyqrc_name(qrc), source = qrc)))
    env.Depends(t, depends)

    return t

def pylupdate4(env, ts, src):
    '''
    Carefully update the translation file ts from the given source files.
    '''
    t = env.Precious(env.NoClean(env.PyLupdate4(target = ts, source = src)))
    env.Depends(t, src)

    return t

def lrelease(env, qm, ts):
    '''
    Carefully generate the "compiled" translation file qm from the given ts
    file(s).
    '''
    t = env.Precious(env.NoClean(env.Lrelease(target = qm, source = ts)))
    env.Depends(t, ts)

    return t
