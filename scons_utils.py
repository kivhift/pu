import os
import tempfile

import PyQt4
from PyQt4.uic import compileUi

pyrcc4_tool = os.path.join(PyQt4.__path__[0], 'pyrcc4')

def carefully_install(env, wohin, was):
    '''
    Install the target was to the location wohin being careful not to
    clobber stuff in the process.
    '''
    return env.Precious(env.NoClean(env.Install(wohin, was)))

def decrlf(target, source, env):
    '''
    Remove those pesky CRLFs from the end of lines.
    '''
    for t in target:
        name = str(t)
        if not os.path.exists(name) or not os.path.isfile(name): continue
        tf = tempfile.TemporaryFile()
        with open(name, 'rb') as f:
            cnt = 0
            for ln in f:
                nln = ln.rstrip() + '\n'
                if ln != nln: cnt += 1
                tf.write(nln)
        if cnt > 0:
            tf.seek(0, os.SEEK_SET)
            with open(name, 'w+b') as f:
                f.write(tf.read())

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

def pyuic4(env, ui):
    '''
    Carefully generate the Python module for the given Qt UI file.
    '''
    return env.Precious(env.NoClean(env.PyUic4(
        target = pyui_name(ui), source = ui)))

def pyrcc4(env, qrc, depends = []):
    '''
    Carefully generate the resource module from the given QRC file with the
    given dependencies.
    '''
    t = env.Precious(env.NoClean(env.PyRcc4(
        target = pyqrc_name(qrc), source = qrc)))
    for d in depends: env.Depends(t, d)

    return t
