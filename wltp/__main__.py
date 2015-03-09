#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""The command-line entry-point for using all functionality of wltp tool.

.. Seealso::
    :func:`main()`
"""

from __future__ import division, unicode_literals

import os, sys, collections, functools, re, glob, shutil, logging
from argparse import ArgumentTypeError
from collections import OrderedDict
import argparse
import pkg_resources as pkg
import ast
from distutils.spawn import find_executable
import json
from textwrap import dedent
from wltp import model, pandel, tkui, utils, __version__ as prog_ver
from wltp.pandel import JsonPointerException
from pandas.core.generic import NDFrame
import six

import jsonschema as jsons
import operator as ops
import pandas as pd


DEBUG   = False
PROG    = 'wltp'

DEFAULT_LOG_LEVEL   = logging.INFO
def _init_logging(loglevel, name='%s-cmd'%PROG, skip_root_level=False):
    logging.basicConfig(level=loglevel)
    
    rlog = logging.getLogger()
    if not skip_root_level:
        ## Force root-level, in case already configured otherwise.
        rlog.setLevel(loglevel)

    log = logging.getLogger(name)
    log.trace = lambda *args, **kws: log.log(0, *args, **kws)
    
    return log

    
log = _init_logging(DEFAULT_LOG_LEVEL)

def main(argv=None):
    """Calculates an engine-map by fitting data-points vectors, use --help for gettting help.

    REMARKS:
    --------
        * All string-values are case-sensitive.
        * Boolean string-values are case insensitive:
            False  : false, off, no,  == 0
            True   : true,  on,  yes, != 0
        * In KEY=VALUE pairs, the values are passed as string.  For other types,
          substitute '=' with:.
            +=     : integer
            *=     : float
            ?=     : boolean
            :=     : parsed as json
            @=     : parsed as python (with eval())

    EXAMPLES:
    ---------
    Assuming a 'vehicle.json' file like this:
        {
            "unladen_mass":1230,
            "test_mass":   1300,
            "v_max":    195,
            "p_rated":  100,
            "n_rated":  5450,
            "n_idle":   950,
            "n_min":    None, # Can be overriden by manufacturer.
            "gear_ratios":      [120.5, 75, 50, 43, 37, 32],
            "resistance_coeffs":[100, 0.5, 0.04],
        }

    then the following examples:

        ## Calculate and print fitted engine map's parameters
        #     for a petrol vehicle with the above engine-point's CSV-table:
        >> %(prog)s -I vehicle.csv file_model_path=/vehicle
        -I vehicle.csv file_frmt=SERIES model_path=/params header@=None \

        ## ...and if no header existed:
        >> %(prog)s -m /vehicle:=n_idle -I engine.csv header@=None

        ## Assume PME column contained normalized-Power in Watts,
        #    instead of P in kW:
        >> %(prog)s -m fuel=petrol -I engine.csv  -irenames X X 'Pnorm (w)'

        ## Read the same table above but without header-row and
        #    store results into Excel file, 1st sheet:
        >> %(prog)s -m fuel=petrol -I engine.csv --icolumns CM PME PMF -I engine_map.xlsx sheetname+=0

        ## Supply as inline-json more model-values required for columns [RPM, P, FC]
        #    read from <stdin> as json 2D-array of values (no headers).
        #    and store results in UTF-8 regardless of platform's default encoding:
        >> %(prog)s -m '/engine:={"fuel":"petrol", "stroke":15, "capacity":1359}' \\
                -I - file_frmt=JSON orient=values -c RPM P FC \\
                -O engine_map.txt encoding=UTF-8


    Now, if input vectors are in 2 separate files, the 1st, 'engine_1.xlsx',
    having 5 columns with different headers than expected, like this:
        OTHER1   OTHER2       N        "Fuel waste"   OTHER3
        0       -1            12       0.14           "some text"
        ...

    and the 2nd having 2 columns with no headers at all and
    the 1st column being 'Pnorm', then it, then use the following command:

        >> %(prog)s -O engine_map -m fuel=petrol \\
                -I=engine_1.xlsx sheetname+=0 \\
                -c X   X   N   'Fuel consumption'  X \\
                -r X   X   RPM 'FC(g/s)'           X \\
                -I=engine_2.csv header@=None \\
                -c Pnorm X
    """

    global log, DEBUG

    program_name    = os.path.basename(sys.argv[0])

    if argv is None:
        argv = sys.argv[1:]

    doc_lines       = main.__doc__.splitlines()
    desc            = doc_lines[0]
    epilog          = dedent('\n'.join(doc_lines[1:]))
    parser = build_args_parser(program_name, prog_ver, desc, epilog)

    opts = parser.parse_args(argv)

    try:
        DEBUG = bool(opts.debug)

        if (DEBUG or opts.verbose > 1):
            opts.strict = True

        if opts.verbose >= 2:
            level = 0
        elif opts.verbose >= 1:
            level = logging.DEBUG
        else:
            level = DEFAULT_LOG_LEVEL
        _init_logging(level, name=program_name)

        log.debug("Args: %s\n  +--Opts: %s", argv, opts)

        if opts.gui:
            app = tkui.TkWltp()
            app.mainloop()
            return
        
        if opts.excel:
            copy_excel_template_files(opts.excel)
            return
        
        if opts.excelrun:
            files_copied = copy_excel_template_files(opts.excelrun)          #@UnusedVariable
            xls_file = files_copied[0]
            
            utils.open_file_with_os(xls_file)
            return
        
        if opts.winmenus:
            add_windows_shortcuts_to_start_menu('winmenus')
            return
        
        opts = validate_file_opts(opts)

        infiles     = parse_many_file_args(opts.I, 'r', opts.irenames)
        log.info("Input-files: %s", infiles)

        outfiles    = parse_many_file_args(opts.O, 'w', None)
        log.info("Output-files: %s", outfiles)

    except (ValueError) as ex:
        if DEBUG:
            log.exception('Cmd-line parsing failed!')
        indent = len(program_name) * " "
        parser.exit(3, "%s: %s\n%s  for help use --help\n"%(program_name, ex, indent))

    ## Main program
    #
    try:
        additional_props = not opts.strict
        mdl = assemble_model(infiles, opts.m)
        log.info("Input Model(strict: %s): %s", opts.strict, utils.Lazy(lambda: model.json_dumps(mdl, 'to_string')))
        mdl = model.validate_model(mdl, additional_props)

        mdl = processor.run(opts, mdl)

        store_model_parts(mdl, outfiles)

    except jsons.ValidationError as ex:
        if DEBUG:
            log.error('Invalid input model!', exc_info=ex)
        indent = len(program_name) * " "
        parser.exit(4, "%s: Model validation failed due to: %s\n%s\n"%(program_name, ex, indent))

    except JsonPointerException as ex:
        if DEBUG:
            log.exception('Invalid model operation!')
        indent = len(program_name) * " "
        parser.exit(4, "%s: Model operation failed due to: %s\n%s\n"%(program_name, ex, indent))



def copy_excel_template_files(dest_dir=None):
    import pkg_resources as pkg
    
    if not dest_dir == None:
        dest_dir = os.getcwd()
    else:
        dest_dir = os.path.abspath(dest_dir)

    try:
        os.mkdir(dest_dir)
        log.info('Created destination-directory(%s).', dest_dir)
    except:
        pass ## Might already exist
    
    files_to_copy = ['excel\WltpExcelRunner.xlsm', 'excel\WltpExcelRunner.py']
    files_to_copy = [pkg.resource_filename('wltp', f) for f in files_to_copy] #@UndefinedVariable
    files_copied = []
    for src_fname in files_to_copy:
        dest_fname = os.path.basename(src_fname)
        fname_genor = utils.generate_filenames(os.path.join(dest_dir, dest_fname))
        dest_fname = next(fname_genor)
        while os.path.exists(dest_fname):
            dest_fname = next(fname_genor)
            
        log.info('Copying `xlwings` template-file: %s --> %s', src_fname, dest_fname)
        shutil.copy(src_fname, dest_fname)
        files_copied.append(dest_fname)
    
    return files_copied


def add_windows_shortcuts_to_start_menu(my_option):
    if sys.platform != 'win32':
        exit('This options can run only under *Windows*!')
    my_cmd_name = PROG
    my_cmd_path = find_executable(my_cmd_name)
    if not my_cmd_path:
        exit("Please properly install the project before running the `--%s` command-option!" % my_option)
        
    win_menu_group = 'Python Wltp Calculator'
    
    wshell = utils.win_wshell()
    startMenu_dir   = utils.win_folder(wshell, "StartMenu")
    myDocs_dir      = utils.win_folder(wshell, "MyDocuments")
    docs_url        = 'http://wltp.readthedocs.org/'
    prog_dir        = os.path.join(myDocs_dir, '%s_%s'%(PROG, prog_ver))
    shcuts = OrderedDict([
        ("Create new Wltp ExcelRunner files.lnk", {
            'target_path':  'cmd',
            'target_args':  '/K wltp --excelrun',
            'wdir':         prog_dir,
            'desc':         'Copy `xlwings` excel & python template files into `MyDocuments` and open the Excel-file, so you can run a batch of experiments.',
            'icon_path':    pkg.resource_filename('wltp.excel', 'ExcelPython.ico'),        #@UndefinedVariable
        }),
        ("Wltp Documentation site.url", {
            'target_path':  docs_url,
        }),
    ])


    try:
        os.makedirs(prog_dir, exist_ok=True)
    except Exception as ex:
        log.exception('Failed creating Program-folder(%s) due to: %s', prog_dir, ex)
        exit(-5)
    
    ## Copy Demos.
    #
    demo_dir = pkg.resource_filename('wltp', 'test')                     #@UndefinedVariable
    demo_files =['*.csv', '*.xls?', '*.bat', 'engine.py', 'cmdline_test.py']
    for g in demo_files:
        for src_f in glob.glob(os.path.join(demo_dir, g)):
            f = os.path.basename(src_f)
            dest_f = os.path.join(prog_dir, f)
            if os.path.exists(dest_f):
                log.trace('Removing previous entry(%s) from existing Program-folder(%s).', f, prog_dir)
                try:
                    os.unlink(dest_f)
                except Exception as ex:
                    log.error('Cannot clear existing item(%s) from Program-folder(%s) due to: %s', dest_f, prog_dir, ex)
                    
            try:
                shutil.copy(src_f, dest_f)
            except Exception as ex:
                log.exception('Failed copying item(%s) in program folder(%s): %s', src_f, prog_dir, ex)

    ## Create a fresh-new Menu-group.
    #
    group_path = os.path.join(startMenu_dir, win_menu_group)
    if os.path.exists(group_path):
        log.trace('Removing all entries from existing StartMenu-group(%s).', win_menu_group)
        for f in glob.glob(os.path.join(group_path, '*')):
            try:
                os.unlink(f)
            except Exception as ex:
                log.warning('Minor failure while removing previous StartMenu-item(%s): %s', f, ex)

    try:
        os.makedirs(group_path, exist_ok=True)
    except Exception as ex:
        log.exception('Failed creating StarMenu-group(%s) due to: %s', group_path, ex)
        exit(-6)
    
    for name, shcut in shcuts.items():
        path = os.path.join(group_path, name)
        log.info('Creating StartMenu-item: %s', path)
        try:
            utils.win_create_shortcut(wshell, path, **shcut)
        except Exception as ex:
            log.exception('Failed creating item(%s) in StartMenu-group(%s): %s', path, win_menu_group , ex)


## The value of file_frmt=VALUE to decide which
#    pandas.read_XXX() and write_XXX() methods to use.
#
#_io_file_modes = {'r':0, 'rb':0, 'w':1, 'wb':1, 'a':1, 'ab':1}
_io_file_modes = {'r':0, 'w':1}
_read_clipboard_methods = (pd.read_clipboard, 'to_clipboard')
_default_pandas_format  = 'AUTO'
_pandas_formats = collections.OrderedDict([
    ('AUTO', None),
    ('CSV', (pd.read_csv, 'to_csv')),
    ('TXT', (pd.read_csv, 'to_csv')),
    ('XLS', (pd.read_excel, 'to_excel')),
    ('JSON', (pd.read_json, 'to_json')),
    ('SERIES', (pd.Series.from_csv, 'to_json')),
])
_known_file_exts = {
    'XLSX':'XLS'
}
def get_file_format_from_extension(fname):
    ext = os.path.splitext(fname)[1]
    if (ext):
        ext = ext.upper()[1:]
        if (ext in _known_file_exts):
            return _known_file_exts[ext]
        if (ext in _pandas_formats):
            return ext

    return None


_default_df_path            = ('/engine_points', '/engine_map')
_default_out_file_append    = False
## When option `-m MODEL_PATH=VALUE` contains a relative path,
# the following is preppended:
_default_model_overridde_path = '/engine/'


_value_parsers = {
    '+': int,
    '*': float,
    '?': utils.str2bool,
    ':': json.loads,
    '@': eval,
    #'@': ast.literal_eval ## best-effort security: http://stackoverflow.com/questions/3513292/python-make-eval-safe
}


_key_value_regex = re.compile(r'^\s*([/_A-Za-z][\w/\.]*)\s*([+*?:@]?)=\s*(.*?)\s*$')
def parse_key_value_pair(arg):
    """Argument-type for syntax like: KEY [+*?:]= VALUE."""

    m = _key_value_regex.match(arg)
    if m:
        (key, type_sym, value) = m.groups()
        if type_sym:
            try:
                value   = _value_parsers[type_sym](value)
            except Exception as ex:
                raise six.reraise(ArgumentTypeError, ("Failed parsing key(%s)%s=VALUE(%s) due to: %s" %(key, type_sym, value, ex)), ex.__traceback__) ## Python-2 :-(

        return [key, value]
    else:
        raise argparse.ArgumentTypeError("Not a KEY=VALUE syntax: %s"%arg)


def parse_column_specifier(arg):
    """Argument-type for --icolumns, syntaxed like: COL_NAME [(UNITS)]."""

    res = pandel.parse_value_with_units(arg)
    if res:
        return res
    
    raise argparse.ArgumentTypeError("Not a COLUMN_SPEC syntax: %s"%arg)


def validate_file_opts(opts):
    ## Check number of input-files <--> related-opts
    #
    dopts = vars(opts)

    if (not opts.I):
        n_infiles = 1
    else:
        n_infiles = len(opts.I)
    rel_opts = ['icolumns', 'irenames']
    for ropt in rel_opts:
        opt_val = dopts[ropt]
        if (opt_val):
            n_ropt = len(opt_val)
            if( n_ropt > 1 and n_ropt != n_infiles):
                raise argparse.ArgumentTypeError("Number of --%s(%i) mismatches number of -I(%i)!"%(ropt, n_ropt, n_infiles))


    return opts


FileSpec = collections.namedtuple('FileSpec', ('io_method', 'fname', 'file', 'frmt', 'path', 'append', 'renames', 'kws'))

def parse_many_file_args(many_file_args, filemode, col_renames=None):
    io_file_indx = _io_file_modes[filemode]

    def parse_file_args(n, fname, *kv_args):
        frmt    = _default_pandas_format
        path    = _default_df_path[io_file_indx]
        append  = _default_out_file_append

        kv_pairs = [parse_key_value_pair(kv) for kv in kv_args]
        pandas_kws = dict(kv_pairs)

        if ('file_frmt' in pandas_kws):
            frmt = pandas_kws.pop('file_frmt')
            if (frmt not in _pandas_formats):
                raise argparse.ArgumentTypeError("Unsupported pandas file_frmt: %s\n  Set 'file_frmt=XXX' to one of %s" % (frmt, list(_pandas_formats.keys())[1:]))


        if (frmt == _default_pandas_format):
            if ('-' == fname or fname == '+'):
                frmt = 'CSV'
            else:
                frmt = get_file_format_from_extension(fname)
            if (not frmt):
                raise argparse.ArgumentTypeError("File(%s) has unknown extension, file_frmt is required! \n  Set 'file_frmt=XXX' to one of %s" % (fname, list(_pandas_formats.keys())[1:]))


        if (fname == '+'):
            method = _read_clipboard_methods[io_file_indx]
            file = ''
        else:
            methods = _pandas_formats[frmt]
            assert isinstance(methods, tuple), methods
            method = methods[io_file_indx]

            if (method == pd.read_excel):
                file = fname
            else:
                file = argparse.FileType(filemode)(fname)

        try:
            path = pandas_kws.pop('model_path')
            if (len(path) > 0 and not path.startswith('/')):
                raise argparse.ArgumentTypeError("Only absolute model-paths (those starting with '/') are supported: %s" % (path))
        except KeyError:
            pass

        try:
            append = pandas_kws.pop('file_append')
            append = utils.str2bool(append)
        except KeyError:
            pass

        ## Here we apply a single --irenames to all input-files.
        #
        if col_renames is None:
            renames = None
        elif len(col_renames) == 1:
            renames = col_renames[0]
        else:
            renames = col_renames[n]
        return FileSpec(method, fname, file, frmt, path, append, renames, pandas_kws)

    if not many_file_args:
        return [] # FIXME: Why enumeration on None does not work?
    return [parse_file_args(n, *file_args) for (n, file_args) in enumerate(many_file_args)]


def load_file_as_df(filespec):
# FileSpec(io_method, fname, file, frmt, path, append, kws)
    method = filespec.io_method
    log.debug('Reading file with: pandas.%s(%s, %s)', method.__name__, filespec.fname, filespec.kws)
    if filespec.file is None:       ## ie. when reading CLIPBOARD
        dfin = method(**filespec.kws)
    else:
        dfin = method(filespec.file, **filespec.kws)

    if (filespec.renames):
        old_cols = dfin.columns
        new_cols = [old if new['name'] == '_' else new['name'] for (old, new) in zip(old_cols, filespec.renames)]

        ## If length of rename-columns differ from DF's.
        #    columns at the end are left unchanged,
        #    but will scream if given more renames!
        #
        new_cols += list(old_cols[len(new_cols):])
        dfin.columns = new_cols


    dfin = dfin.convert_objects(convert_numeric=True)

    return dfin


def load_model_part(mdl, filespec):
    dfin = load_file_as_df(filespec)
    log.debug("  +-input-file(%s):\n%s", filespec.fname, dfin.head())
    if filespec.path:
        pandel.set_jsonpointer(mdl, filespec.path, dfin)
    else:
        mdl = dfin
    return mdl


def assemble_model(infiles, model_overrides):

    mdl = model._get_model_base()

    for filespec in infiles:
        try:
            mdl = load_model_part(mdl, filespec)
        except Exception as ex:
            raise six.reraise(Exception, ("Failed reading %s due to: %s" %(filespec, ex)), ex.__traceback__) ## Python-2 :-(

    if (model_overrides):
        model_overrides = functools.reduce(lambda x,y: x+y, model_overrides) # join all -m
        for (json_path, value) in model_overrides:
            try:
                if (not json_path.startswith('/')):
                    json_path = _default_model_overridde_path + json_path
                pandel.set_jsonpointer(mdl, json_path, value)
            except Exception as ex:
                raise six.reraise(Exception, ("Failed setting model-value(%s) due to: %s" %(json_path, value, ex)), ex.__traceback__) ## Python-2 :-(

    return mdl


def store_part_as_df(filespec, part):
    '''If part is Pandas, store it as it is, else, store it as json recursively.

        :param FileSpec filespec: named_tuple
        :param part: what to store, originating from model(filespec.path))
    '''

    if isinstance(part, NDFrame):
        log.debug('Writing file with: pandas.%s(%s, %s)', filespec.io_method, filespec.fname, filespec.kws)
        if filespec.file is None:       ## ie. when reading CLIPBOARD
            method = ops.methodcaller(filespec.io_method, **filespec.kws)
        else:
            method = ops.methodcaller(filespec.io_method, filespec.file, **filespec.kws)
        method(part)
    else:
        model.json_dump(part, filespec.file, pd_method=None, **filespec.kws)


def store_model_parts(mdl, outfiles):
    for filespec in outfiles:
        try:
            try:
                part = pandel.resolve_jsonpointer(mdl, filespec.path)
            except JsonPointerException:
                log.warning('Nothing found at model(%s) to write to file(%s).', filespec.path, filespec.fname)
            else:
                store_part_as_df(filespec, part)
        except Exception as ex:
            raise six.reraise(Exception, ("Failed storing %s due to: %s" %(filespec, ex)), ex.__traceback__) ## Python-2 :-(

class RawTextHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Help message formatter which retains formatting of all help text.

    Only the name of this class is considered a public API. All the methods
    provided by the class are considered an implementation detail.
    """

    def _split_lines(self, text, width):
        return text.splitlines()


def build_args_parser(program_name, version, desc, epilog):
    version_string  = '%s' % version

    parser = argparse.ArgumentParser(prog=program_name, description=desc, epilog=epilog, add_help=False,
                                     formatter_class=RawTextHelpFormatter)


    grp_io = parser.add_argument_group('Input/Output', 'Options controlling reading/writting of file(s) and for specifying model values.')
    grp_io.add_argument('-I', help=dedent("""\
            import file(s) into the model utilizing pandas-IO methods, see
                http://pandas.pydata.org/pandas-docs/stable/io.html
            Default: %(default)s]
            * The syntax of this option is like this:
                    FILENAME [KEY=VALUE ...]]
            * The FILENAME can be '-' to designate <stdin> or '+' to designate CLIPBOARD.
            * Any KEY-VALUE pairs pass directly to pandas.read_XXX() options,
              except from the following keys, which are consumed before reaching pandas:
                ** file_frmt = [ AUTO | CSV | TXT | XLS | JSON | SERIES ]
                  selects which pandas.read_XXX() method to use:
                    *** AUTO: the format is deduced from the filename's extension (ie Excel files).
                    *** JSON: different sub-formats are selected through the 'orient' keyword
                      of Pandas specified with a key-value pair
                      (see: http://pandas.pydata.org/pandas-docs/dev/generated/pandas.io.json.read_json.html).
                    *** SERIES: uses `pd.Series.from_csv()`.
                    *** Defaults to AUTO, unless reading <stdin> or <clipboard>, which then is CSV.
                ** model_path = MODEL_PATH
                  specifies the destination (or source) of the dataframe within the model
                  as json-pointer path (see -m option).
                  If many input-files have the same --model_path, the dataframes are
                  concatenated horizontally, therefore the number of rows (excluding header)
                  for all those data-files must be equal.
            * When multiple input-files given, the number of --icolumns and --irenames options,
              must either match them, be 1 (meaning, use them for all files), or be totally absent
              (meaning, use defaults for all files).
            * see REMARKS at the bottom regarding the parsing of KEY-VAULE pairs. """),
                        action='append', nargs='+', 
                        #default=[('- file_frmt=%s model_path=%s'%('CSV', _default_df_dest)).split()],
                        metavar='ARG')
    grp_io.add_argument('-c', '--icolumns', help=dedent("""\
            describes the columns-contents of input file(s) along with their units (see --I).
            It must be followed either by an integer denoting the index of the header-row
            within the tabular data, or by a list of column-names specifications,
            obeying the following syntax:
                COL_NAME [(UNITS)]
            Accepted quantities and their default units are grouped in 3+1 quantity-types and
            for each file exactly one from each of the 3 first categories must be present:
            1. engine-speed:
                RPM      (rad/min)
                RPMnorm  (rad/min)  : normalized against RPMnorm * RPM_IDLE + (RPM_RATED - RPM_IDLE)
                Omega    (rad/sec)
                CM       (m/sec)    : Mean Piston speed
            2. work-capability:
                P        (kW)
                Pnorm    (kW)       : normalized against P_MAX
                T        (Nm)
                PME      (bar)
            3. fuel-consumption:
                FC       (g/h)
                FCnorm   (g/h)      : normalized against P_MAX
                PMF      (bar)
            4. Irellevant column:
                X
            Default when files include headers is 0 (1st row), otherwise it is 'RPM,P,FC'."""),
                        action='append', nargs='+',
                        type=parse_column_specifier, metavar='COLUMN_SPEC')
    grp_io.add_argument('-r', '--irenames', help=dedent("""\
            renames the columns of input-file(s)  (see --I).
            It must be followed by a list of column-names specifications like --icolumns,
            but without accepting integers.
            The number of renamed-columns for each input-file must be equal or less
            than those in the --icolumns for the respective inpute-file.
            Use '_' for columns to be left intact."""),
                        action='append', nargs='*',
                        type=parse_column_specifier, metavar='COLUMN_SPEC')
    grp_io.add_argument('-m', help=dedent("""\
            override a model value.
            * The MODEL_PATH is a json-pointer absolute or relative path, see:
                    https://python-json-pointer.readthedocs.org/en/latest/tutorial.html
              Relative paths are resolved against '/engine', for instance:
                    -Mrpm_idle=850   -M/engine/p_max=660
              would set the following model's property:
                    {
                      "engine": {
                          "rpm_idle": 850,
                          "p_max": 660,
                          ...
                      }
                    }
            * Any values from -m options are applied AFTER any files read by -I option.
            * See REMARKS below for the parsing of KEY-VAULE pairs.
            """),
                        action='append', nargs='+',
                        type=parse_key_value_pair, metavar='MODEL_PATH=VALUE')
    grp_io.add_argument('--strict', help=dedent("""\
            validate model more strictly, ie no additional-properties allowed.
            [default: %(default)s]"""),
            default=False, type=utils.str2bool,
            metavar='[TRUE | FALSE]')
    grp_io.add_argument('-M', help=dedent("""\
            get help description for the specfied model path.
            If no path specified, gets the default model-base. """),
                        action='append', nargs='*',
                        type=parse_key_value_pair, metavar='MODEL_PATH')


    grp_io.add_argument('-O', help=dedent("""\
            specifies output-file(s) to write model-portions into after calculations.
            The syntax is indentical to -I, with these differences:
            * Instead of <stdin>, <stdout> and write_XXX() methods are used wherever.
            * One extra key-value pair:
            ** file_append = [ TRUE | FALSE ]
                    specify whether to augment pre-existing files, or overwrite them.
            * Default: - file_frmt=CSV model_path=/engine_map """),
                        action='append', nargs='+',
                        #default=[('- file_frmt=%s model_path=%s file_append=%s'%('CSV', _default_df_path[1],  _default_out_file_append)).split()],
                        metavar='ARG')


    xlusive_group = parser.add_mutually_exclusive_group()
    xlusive_group.add_argument('--gui', help='start GUI to run a single experiment', action='store_true')
    xlusive_group.add_argument('--excel', help="copy `xlwings` excel & python template files into DESTPATH or current-working dir, to run a batch of experiments", 
        nargs='?', const=None, metavar='DESTPATH')
#    xlusive_group.add_argument('--excelrun', help="Copy `xlwings` excel & python template files into USERDIR and open Excel-file, to run a batch of experiments", 
#        nargs='?', const=os.getcwd(), metavar='DESTPATH')
    xlusive_group.add_argument('--winmenus', help="Adds shortcuts into Windows StartMenu.", action='store_true')
    
    grp_various = parser.add_argument_group('Various', 'Options controlling various other aspects.')
    grp_various.add_argument('-d', "--debug", action="store_true", help=dedent("""\
            set debug-mode with various checks and error-traces
            Suggested combining with --verbose counter-flag.
            Implies --strict true
            [default: %(default)s] """),
                        default=False)
    grp_various.add_argument('-v', "--verbose", action="count", default=0, help="set verbosity level [default: %(default)s]")
    grp_various.add_argument("--version", action="version", version=version_string, help="prints version identifier of the program")
    grp_various.add_argument("--help", action="help", help='show this help message and exit')

    return parser



if __name__ == "__main__":
    main()
