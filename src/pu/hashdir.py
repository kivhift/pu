#!/usr/bin/python

import hashlib
import io
import os
import tempfile

def files_differ(A, B):
    if os.stat(A).st_size != os.stat(B).st_size: return True

    differ_status = False
    A_fi = B_fi = None
    sz = io.DEFAULT_BUFFER_SIZE
    try:
        A_fi, B_fi = open(A, 'rb'), open(B, 'rb')
        while True:
            A_buf, B_buf = A_fi.read(sz), B_fi.read(sz)
            if A_buf != B_buf:
                differ_status = True
                break
            if len(A_buf) < sz: break
    finally:
        if A_fi is not None: A_fi.close()
        if B_fi is not None: B_fi.close()

    return differ_status

def add_file(addee, rootdir = ''):
    if rootdir and not os.path.exists(rootdir):
        raise ValueError('Directory not there: ' + rootdir)
    if rootdir and not os.path.isdir(rootdir):
        raise ValueError('Not directory: ' + rootdir)

    fi = fdo = None
    try:
        if type(addee) in (str, unicode):
            fi = open(addee, 'rb')
        else:
            fi = addee

        fdo, fdo_name = tempfile.mkstemp(dir = rootdir)

        sz = io.DEFAULT_BUFFER_SIZE
        fhash = hashlib.sha1()
        while True:
            buf = fi.read(sz)
            os.write(fdo, buf)
            fhash.update(buf)
            if len(buf) < sz: break
    finally:
        if fi is not None and id(fi) != id(addee): fi.close()
        if fdo is not None: os.close(fdo)

    digest = fhash.hexdigest()
    pre, rest = digest[0:2], digest[2:]

    fdir = os.path.join(rootdir, pre)
    if not os.path.exists(fdir): os.mkdir(fdir)

    targ = os.path.join(fdir, rest)
    if os.path.exists(targ):
        if files_differ(fdo_name, targ):
            raise RuntimeError('Addee collided with extant file: %s, %s' % (
                fdo_name, targ))
        os.unlink(fdo_name)
    else:
        os.rename(fdo_name, targ)

    return os.path.join(pre, rest)
