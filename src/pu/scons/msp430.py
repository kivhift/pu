#
# Copyright (c) 2013 Joshua Hughes <kivhift@gmail.com>
#
from glob import glob
from os.path import join
from subprocess import list2cmdline

def IAREnvironment(ew_version = '*', core = '430', data_model = None,
        part = None, double_size = None, hw_mult = None, optimization = None,
        listing_dir = None, fill = None, msp430_txt = False, includes = None):
    """Produce an SCons Environment tailored around IAR's MSP430 tools.

    Most of the arguments are passed through to the underlying IAR tools.  Here
    are the available options:
        - `ew_version`: ``*`` or the specific version number
        - `core`: ``430`` or ``430X``
        - `data_model`: if ``430X`` is given for `core`, then `data_model` must
          be one of ``s``, ``m`` or ``l`` for a small, medium or large data
          model
        - `part`: the MSP430 part number; e.g., ``fr5969``
        - `double_size`: 32 or 64
        - `hw_mult`: one of ``mult``, ``mult32`` or ``mult32_alt``
        - `optimization`: one of ``n``, ``l``, ``m``, ``h``, ``hs`` or ``hz``
        - `listing_dir`: directory to output listings to
        - `fill`: hex value to fill unused memory with; e.g., ``3fff``
        - `msp430_txt`: set to `True` to also output MSP430 text
        - `includes`: list of directories to add to include path

    Only `ew_version` and `core` must be specified.  If the rest of the
    arguments aren't specified, then the feature is not enabled or the default
    value is used if needed.
    """

    # The SCons stuff isn't normally importable.  (It's taken care of when
    # building.)  So, import the stuff here so as to allow the module to be
    # imported normally (i.e., via the REPL, Sphinx, etc.).
    from SCons.Defaults import ASAction
    from SCons.Environment import Environment

    candidates = glob(
        r'C:\Program Files\IAR Systems\Embedded Workbench ' + ew_version)
    if not candidates: raise ValueError('Embedded workbench not found.')
    candidates.sort()
    ewb = candidates[-1]
    def join_ewb(*a): return join(ewb, *a)
    def base_quoted(*a): return list2cmdline((join_ewb(*a),))
    binp = join(*'430 bin'.split())
    a430 = base_quoted(binp, 'a430')
    icc430 = base_quoted(binp, 'icc430')
    xlink = base_quoted(binp, 'xlink')
    clib = '430 lib clib cl'

    e = Environment(
        AS = a430,
        ASFLAGS = [],
        CC = icc430,
        CCCOM = '$CC -o $TARGET $CFLAGS $CCFLAGS $_CCCOMCOM $SOURCES',
        CFLAGS = [],
        CPPPATH = [],
        INCPREFIX = '-I ',
        LINK = xlink,
        LINKCOM = (
            '$LINK -o $TARGET $_LIBDIRFLAGS $_LIBFLAGS $LINKFLAGS $SOURCES '),
        LINKFLAGS = [],
        OBJSUFFIX = '.r43',
        PROGSUFFIX = '.d43',
        TOOLS = ['as', 'cc', 'link']
    )

    # SCons doesn't know about this extension for assembly files.
    e['BUILDERS']['Object'].add_action('.s43', ASAction)

    # Set up the base arguments to be augmented by the given arguments below.
    aflags = '-M() -s+ -t8 -ws -r'.split()
    cflags = '''--clib --diag_suppress Pa050 --warnings_are_errors -r
        --char_is_unsigned --require_prototypes
        --macro_positions_in_diagnostics'''.split()
    lflags = '''-r'''.split()
    afe, cfe, lfe = aflags.extend, cflags.extend, lflags.extend

    core = core.lower()
    clib += core
    if '430' == core:
        afe(['-v0'])
        cfe(['--core=430'])
    elif '430x' == core:
        if not data_model: data_model = 's'
        clib += data_model
        afe(['-v1'])
        cfe(['--core=430X', '--data_model={}'.format(
            dict(s = 'small', m = 'medium', l = 'large')[data_model])])
    else:
        raise ValueError('Invalid core specification: {}'.format(core))

    cfg_dir = join(*'430 config'.split())
    if part:
        # In the IAR-supplied files, the stack size and heap size aren't
        # defined so we'll need to include them.  The linker also needs to be
        # told that the library-supplied boot code is in __program_start().
        lfe('''-D_STACK_SIZE=80 -D_DATA16_HEAP_SIZE=80 -D_DATA20_HEAP_SIZE=80
            -s __program_start -f'''.split())
        lfe([join_ewb(cfg_dir, 'lnk430{}.xcl'.format(part))])
    else:
        lfe(['-cmsp430'])

    if not double_size: double_size = 32
    clib += {32 : 'f', 64 : 'd'}[double_size] + '.r43'
    cfe(['--double={}'.format(double_size)])

    if hw_mult:
        lfe(['-f', join_ewb(join(cfg_dir, dict(
            mult = 'multiplier.xcl',
            mult32 = 'multiplier32.xcl',
            mult32_alt = 'multiplier32_loc2.xcl')[hw_mult]))])
        cfe(['--multiplier={}'.format(
            32 if hw_mult.startswith('mult32') else 16)])

    if optimization:
        cfe(['-O{}'.format(optimization)])

    if listing_dir:
        afe('-L{} -cM'.format(listing_dir).split())
        cfe('-lA {0} -lC {0}'.format(listing_dir).split())
        lfe('-L -xeims'.split())

    if fill:
        lfe(['-H{}'.format(fill)])

    if msp430_txt:
        lfe(['-Omsp430_txt'])

    if includes:
        e.Append(CPPPATH = includes)
        afe(['-I{}'.format(p) for p in includes])

    # Make sure that clib is given after our objects so that library
    # replacements are possible.  Otherwise, the library code is found first
    # and linked.
    e['LINKCOM'] += base_quoted(*clib.split())
    e.Append(ASFLAGS = aflags, CFLAGS = cflags, LINKFLAGS = lflags)

    return e
