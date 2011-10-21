#!/usr/bin/python

import hashlib
import io
import os
import tempfile

def files_differ(A, B):
    '''
    Return True if the content of the two files differ, False otherwise.
    '''
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

def get_dir_name_from_hexdigest(digest):
    return digest[0:2]

def get_file_name_from_hexdigest(digest):
    return digest[2:]

def get_path_from_hexdigest(digest):
    return os.path.join(get_dir_name_from_hexdigest(digest),
        get_file_name_from_hexdigest(digest))

def add_file(addee, rootdir = '.', rename = False):
    '''
    Add the given file to the given hash directory and return the hex digest
    thereof.  The addee can be given as either a file name or a file-like
    object.  If rename_file is True and addee is an already extant file,
    then it is moved to the new location instead of a copy of it.
    '''
    if rootdir and not os.path.exists(rootdir):
        raise ValueError('Directory not there: ' + rootdir)
    if rootdir and not os.path.isdir(rootdir):
        raise ValueError('Not directory: ' + rootdir)

    fi = fdo = None
    rename_addee = False
    try:
        if type(addee) in (str, unicode):
            fi = open(addee, 'rb')
            rename_addee = rename
        else:
            fi = addee

        if not rename_addee:
            fdo, fdo_name = tempfile.mkstemp(dir = rootdir)
        else:
            fdo_name = addee

        sz = io.DEFAULT_BUFFER_SIZE
        fhash = hashlib.sha1()
        while True:
            buf = fi.read(sz)
            if not rename_addee: os.write(fdo, buf)
            fhash.update(buf)
            if len(buf) < sz: break
    finally:
        if fi is not None and id(fi) != id(addee): fi.close()
        if fdo is not None: os.close(fdo)

    digest = fhash.hexdigest()

    fdir = os.path.join(rootdir, get_dir_name_from_hexdigest(digest))
    if not os.path.exists(fdir): os.mkdir(fdir)

    targ = os.path.join(rootdir, get_path_from_hexdigest(digest))
    if os.path.exists(targ):
        if files_differ(fdo_name, targ):
            raise RuntimeError('Addee collided with extant file: %s, %s' % (
                fdo_name, targ))
        os.unlink(fdo_name)
    else:
        os.rename(fdo_name, targ)

    return digest

class HashDir(object):
    def __init__(self, rootdir = '.', rename = False):
        self.rootdir = rootdir
        self.rename = rename

    def addFile(self, addee):
        '''Add addee to the hashdir and return the hex digest thereof.'''
        return add_file(addee, self.rootdir, self.rename)

    def pathFromHexDigest(self, digest):
        '''Get the path to the file associated with the given digest.'''
        return os.path.join(self.rootdir, get_path_from_hexdigest(digest))

    def openFileFromHexDigest(self, digest):
        '''Open the file associated with the given digest for reading.'''
        return open(self.pathFromHexDigest(digest), 'rb')
