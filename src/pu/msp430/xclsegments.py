#
# Copyright (c) 2012-2013 Joshua Hughes <kivhift@gmail.com>
#
"""
Generate XCL files for segments for IAR's xlink.

In keeping with DRY, this module takes files that define various segments for
IAR-produced firmware and outputs both the XCL files for use with xlink and
headers for use within the firmware in question.

"""
import os

from pu.utils import import_code, is_a_string

class Segment(object):
    """
    Encapsulate a generic segment of memory.

    To make the segment files easier to specify, this class wraps the needed
    information for a given segment and supplies methods to check for overlap,
    return the needed XCL segment argument, etc.

    """
    def __init__(self, start_addr, end_addr, name, type_ = 'CONST'):
        if start_addr > end_addr:
            raise ValueError(
                'Start address > end address: {:x} {:x}'.format(
                    start_addr, end_addr))

        if not name or not is_a_string(name):
            raise ValueError('Invalid name: {}'.format(name))

        seg_types = 'CODE CONST DATA'.split()
        if type_ not in seg_types:
            raise ValueError('Invalid segment type: {}'.format(type_))

        self.start_addr = start_addr
        self.end_addr = end_addr
        self.name = name
        self.type_ = type_

    def __cmp__(self, other):
        """Compare two segments based on their start addresses."""
        if self.start_addr < other.start_addr:
            return -1
        elif self.start_addr == other.start_addr:
            return 0

        return 1

    def __repr__(self):
        return '{}(0x{:x}, 0x{:x}, {}, {})'.format(self.__class__.__name__,
            self.start_addr, self.end_addr, repr(self.name), repr(self.type_))

    def __str__(self):
        """Return the XCL segment specification."""
        return '-Z({type_}){name}={start_addr:x}-{end_addr:x}'.format(
            **self.__dict__)

    def __len__(self):
        return 1 + self.end_addr - self.start_addr

    def __xor__(self, other):
        """
        Return the intersection of `self` and `other`.

        If `self` and `other` overlap, then a new :class:`Segment` is returned
        with their intersection.  If not, then None is returned.

        """
        A, B = self, other

        if A > B:
            A, B = B, A

        if 0 > (A.end_addr - B.start_addr):
            return None

        return self.__class__(B.start_addr, min(A.end_addr, B.end_addr),
            '{}^{}'.format(self.name, other.name))

    def __or__(self, other):
        """
        Return the union of `self` and `other`.

        A tuple is always returned with either a single :class:`Segment` with
        the union of `self` and `other` if they overlap or just `self` and
        `other`.  In the special case where the segments are adjacent but not
        overlapping, a tuple with a single :class:`Segment` is returned with
        `self` and `other` merged together.  The tuples returned are always
        ordered by starting address.

        """
        if other is None: return self,

        A, B = self, other
        fmt = '{}|{}'.format

        if A > B:
            A, B = B, A

        if A ^ B is None:
            if (A.end_addr + 1) == B.start_addr:
                return self.__class__(A.start_addr, B.end_addr,
                    fmt(self.name, other.name)),
            else:
                return A, B

        return self.__class__(A.start_addr, max(A.end_addr, B.end_addr),
            fmt(self.name, other.name)),

def segment_definitions(seg_file):
    """
    Load `seg_file` and return a module with the contents.

    The file is expected to specify at least the RAM and general non-volatile
    segments as `ram` and `general_nv`, respectively.  Other segments are
    specified in a list `segments`.  The segments are checked for overlap.

    """
    with open(seg_file, 'rb') as f:
        sd = import_code(f, 'segdefs', globals_ = globals())

    if not hasattr(sd, 'ram'):
        raise AttributeError('The RAM segment is missing.')

    if not hasattr(sd, 'general_nv'):
        raise AttributeError('The general non-volatile segment is missing.')

    if not hasattr(sd, 'segments'): sd.segments = []

    mem = [sd.ram]
    for seg in sd.segments + [sd.general_nv]:
        ia = 0
        for i, mi in enumerate(mem):
            segim = seg ^ mi
            if segim is not None:
                raise ValueError('Overlap detected: %r' % segim)
            if seg >= mi:
                ia = i
        segumem = mem.pop(ia) | seg
        for i, si in enumerate(segumem):
            mem.insert(ia + i, si)
        ia += i
        if (ia + 1) < len(mem):
            segumem = mem.pop(ia) | mem.pop(ia)
            for i, si in enumerate(segumem):
                mem.insert(ia + i, si)

    n = {}
    for seg in sd.segments + [sd.ram, sd.general_nv]: n[seg.name] = seg
    sd.segments_by_name = n

    return sd

def segment_definitions_to_xcl(seg_file, xcl_file):
    """Produce an XCL file in `xcl_file` from `seg_file`."""

    sd = segment_definitions(seg_file)
    with open(xcl_file, 'wb') as f:
        f.write('''\
-Z(DATA)DATA16_I,DATA16_Z,DATA16_N,HEAP+_HEAP_SIZE={0}
-Z(DATA)CSTACK+_STACK_SIZE#
-Z(CONST)DATA16_C,DATA16_ID,DIFUNCT={1}
-Z(CONST)DATA20_C,DATA20_ID={1}
-Z(CODE)CSTART,ISR_CODE={1}
-P(CODE)CODE={1}
'''.format('{0.start_addr:x}-{0.end_addr:x}'.format(sd.ram),
            '{0.start_addr:x}-{0.end_addr:x}'.format(sd.general_nv)))
        for seg in sd.segments:
            f.write(str(seg))
            f.write('\n')

        if hasattr(sd, 'xcl_passthrough'):
            f.write('\n'.join(sd.xcl_passthrough))
            f.write('\n')

def segment_definitions_to_C_header(seg_file, header_file, guard = None,
        pre = None):
    """
    Produce a C header file in `header_file` from `seg_file`.

    The include guard can be specified via `guard`.  If it is None, then the
    include guard is derived from the base name of `header_file`.  The name
    prefix can be specified via `pre`.  If it is None, then the prefix ``SEG_``
    is used.

    """
    sd = segment_definitions(seg_file)
    with open(header_file, 'wb') as f:
        if guard is None:
            guard = os.path.basename(
                header_file).upper().replace('.', '_').replace('-', '_')
        if pre is None:
            pre = '#define SEG_'
        else:
            pre = '#define ' + pre
        f.write('/* Automatically generated from {}. */\n'.format(
            os.path.basename(seg_file)))
        f.write('#ifndef {0}\n#define {0}\n'.format(guard))

        for seg in [sd.ram, sd.general_nv] + sd.segments:
            f.write('{0}{1.name} (0x{1.start_addr:x})\n'.format(pre, seg))
            f.write('{0}{1.name}_SIZE (0x{2:x})\n'.format(pre, seg, len(seg)))

        if hasattr(sd, 'cheader_passthrough'):
            f.write('\n'.join(sd.cheader_passthrough))
            f.write('\n')

        f.write('#endif/*{}*/\n'.format(guard))

def setup_segment_builders(env, builder_factory):
    """Setup the SCons XCL and header builders for `env`."""

    def build_xcl(target, source, env):
        segment_definitions_to_xcl(str(source[0]), str(target[0]))

    def build_c_header(target, source, env):
        segment_definitions_to_C_header(str(source[0]), str(target[0]))

    builders = env['BUILDERS']
    builders['SegmentXCL'] = builder_factory(action = build_xcl)
    builders['SegmentCHeader'] = builder_factory(action = build_c_header)

def segmentXCL(env, targ, src):
    t = env.Precious(env.NoClean(env.SegmentXCL(target = targ, source = src)))
    env.Depends(t, src)

    return t

def segmentCHeader(env, targ, src):
    t = env.Precious(env.NoClean(env.SegmentCHeader(
        target = targ, source = src)))
    env.Depends(t, src)

    return t
