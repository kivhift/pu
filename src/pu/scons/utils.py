#!/usr/bin/python
#
# Copyright (c) 2010-2012 Joshua Hughes <kivhift@gmail.com>
#
import os
import tempfile

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
