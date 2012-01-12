import os
import tempfile

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
