#
# Copyright (c) 2010-2014 Joshua Hughes <kivhift@gmail.com>
#
import contextlib
import os
import tarfile
import tempfile
import zipfile

from pu.utils import import_code, is_a_string

def carefully_install(env, wohin, was):
    '''
    Install the target was to the location wohin being careful not to
    clobber stuff in the process.
    '''
    return env.Precious(env.NoClean(env.Install(wohin, was)))

def be_careful_with(env, was):
    '''Make sure that the given target was isn't clobbered.'''
    return env.Precious(env.NoClean(was))

def fix_trailing_whitespace(target, source, env):
    '''
    Remove trailing whitespace from the end of lines.
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

decrlf = fix_trailing_whitespace

def _add_base(base, name):
    return '/'.join([base, name])

def _load_archive_config(src):
    with open(src.path) as f:
        cfg = import_code(f, os.path.splitext(src.name)[0])

    if not hasattr(cfg, 'archive_config'):
        raise AttributeError('No archive_config in {}.'.format(src.path))

    return cfg

def tar_gz_from_config(target, source, env):
    '''
    This function produces a gzipped tar archive target from the config
    file given in source.  The config file is simply a Python module that
    should have an iterable called archive_config which produces items that
    are either names or name/archive-name pairs (that can be indexed).  The
    name/archive-name pairs are used to specify the name in the archive for
    the given file/directory being added.  The target name is used to
    arrive at a top-level directory name for the archive.  Directories are
    added recursively.

    The following config file produces the following archive structure
    (assuming that the files are extant, etc. and that the target name is
    x.tgz):

        archive_config = ['a', 'b/c', ['d', 'e']]

        x/a
        x/b/c
        x/e
    '''
    t = str(target[0])
    if t.endswith('.tgz'):
        base = t[:-4]
    elif t.endswith('.tar.gz'):
        base = t[:-7]
    else:
        base = os.path.splitext(t)[0]
    base = os.path.basename(base)
    add_base = lambda name: _add_base(base, name)

    cfg = _load_archive_config(source[0])

    with contextlib.closing(tarfile.open(name = t, mode = 'w:gz')) as tf:
        for f in cfg.archive_config:
            if is_a_string(f):
                tf.add(f, add_base(f))
            else:
                tf.add(f[0], add_base(f[1]))

def zip_from_config(target, source, env):
    """Produce a zip file `target` from the config file in `source`.

    See the documentation for :func:`tar_gz_from_config` for the format of
    the config file.
    """

    t = str(target[0])
    base = os.path.basename(os.path.splitext(t)[0])
    add_base = lambda name: _add_base(base, name)
    join = lambda x, y: '/'.join([x,y])

    cfg = _load_archive_config(source[0])

    with zipfile.ZipFile(t, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in cfg.archive_config:
            if is_a_string(f):
                fn, an = f, add_base(f)
            else:
                fn, an = f[0], add_base(f[1])
            z.write(fn, an)
            # It would be nice if you could add directories recursively.  Oh
            # well...
            if os.path.isdir(fn):
                toadd = os.listdir(fn)
                while toadd:
                    entry = toadd.pop(0)
                    fne = join(fn, entry)
                    z.write(fne, join(an, entry))
                    if os.path.isdir(fne):
                        toadd.extend(join(entry, x) for x in os.listdir(fne))

def always_build(dependency, target, prev_ni):
    """Decide to always build.

    If this function is feed to SCons's ``Decider()``, then all targets will
    be built each time that ``scons`` is executed.  This can be used per
    target by cloning environments and feeding this function to the
    per-environment ``Decider()``.

    """

    return True
