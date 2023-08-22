import argparse
import logging
import traceback
import glob
import os
import sys
import subprocess
import re
import json

from .find_qmldom import find_qmldom
from .qmldom import QMLDom
from .annotate import pre_annotate, final_annotate
from .report import generate_report
from .parse_coverage import parse_coverage

def instrument(args, logger, debug):
    globs = args.glob
    if not globs or len(globs) == 0:
        globs = ['./**/*.qml']
    def do_glob(path):
        logger.debug('Globbing: {}'.format(path))
        return glob.glob(path, recursive=True)
    
    qml_files = [do_glob(g) for g in globs]
    # flatten
    qml_files = [item for sublist in qml_files for item in sublist]
    if len(qml_files) == 0:
        logger.error('No QML files found. Please provide (a) globbing path(s) to the QML files with --path.')
        exit(1)
    logger.debug('QML files: {}'.format(qml_files))
    logger.info('Found {} QML files'.format(len(qml_files)))
    
    qmldom_path = args.qmldom
    if not qmldom_path:
        logger.debug('No qmldom path provided. Trying to find it automatically.')
        qmldom_path = find_qmldom()
    if not qmldom_path:
        logger.error("Could not find qmldom executable. Please provide the path manually with --qmldom.")
        exit(1)
    qmldom = QMLDom(qmldom_path)
    
    for qml_file in qml_files:
        logger.debug('Pre-annotating: {}'.format(qml_file))

        contents = None
        with open(qml_file, 'r') as f:
            contents = f.read()

        out_file = ''
        if args.in_place:
            if not args.no_backups:
                with open('{}.qoverage.bkp'.format(qml_file), 'w') as f:
                    f.write(contents)
            out_file = qml_file
        elif args.output_path:
            if not args.glob_base:
                logger.error('Cannot use --out-path without --glob-base.')
                exit(1)
            subpath = os.path.relpath(os.path.abspath(qml_file), os.path.abspath(args.glob_base))
            out_file = os.path.join(args.output_path, subpath)

        try:
            pre_annotated = pre_annotate(contents, qmldom, debug=debug)
            db_js_filename = out_file + '.qoverage.js'
            annotated,runtime_db_js = final_annotate(pre_annotated, os.path.basename(db_js_filename), debug=debug)
            with open(out_file, 'w') as f:
                f.write(annotated)
            with open(db_js_filename, 'w') as f:
                f.write(runtime_db_js)
            if args.store_intermediates:
                with open(out_file + '.qoverage.pre', 'w') as f:
                    f.write(pre_annotated)
        except Exception as e:
            logger.error('Failed to instrument {}: {}. Skipping.'.format(qml_file, e))
            continue
    
def collect(maybe_filename, maybe_cmd, basedir, report_filename, logger):
    if maybe_cmd and maybe_filename:
        raise Exception("Both a filename and a command were passed. Parsing can be done either on a file or on the output of a command, but not both.")
    if not maybe_cmd and not maybe_filename:
        raise Exception("Neither a filename nor a command were passed. Parsing can be done either on a file or on the output of a command.")

    lines = []
    if maybe_filename:
        logger.info('Parsing: {}'.format(maybe_filename))
        with open(maybe_filename, 'r') as f:
            lines = f.readlines()
    elif maybe_cmd:
        logger.info('Running: {}'.format(' '.join(maybe_cmd)))
        p = subprocess.Popen(maybe_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout:
            line = line.decode('utf-8')
            print(line, end='')
            lines.append(line)
        p.wait()
    
    # Run but record stdout for coverage reports
    coverages = {}
    coverages = parse_coverage(lines, coverages)

    # Put 0 coverage data for files that were not collected
    all_tracked_files = glob.glob('{}/**/*.qoverage.js'.format(basedir), recursive=True)
    for tracked_file_db in all_tracked_files:
        tracked_file = tracked_file_db.replace('.qoverage.js', '')
        if not tracked_file in coverages:
            logger.debug('File was never loaded: {}. Inserting 0 coverage.'.format(tracked_file))
            with open(tracked_file_db, 'r') as f:
                contents = f.read()
                
                n_lines = None
                include_lines = None

                match = re.search(r'const n_lines = (\d+)', contents)
                if not match:
                    raise Exception('Could not find n_lines in file: {}'.format(tracked_file))
                try:
                    n_lines = int(match.group(1))
                except Exception as e:
                    raise Exception('Could not parse n_lines in file: {}'.format(str(e)))
                
                match = re.search(r'const include_lines = (.*)', contents)
                if not match:
                    raise Exception('Could not find include_lines in file: {}'.format(tracked_file))
                try:
                    include_lines = json.loads(match.group(1))
                except Exception as e:
                    raise Exception('Could not parse include_lines in file: {}'.format(str(e)))


                this_file_cov = [None] * n_lines
                for line in include_lines:
                    this_file_cov[line] = 0
                   
                coverages[tracked_file] = json.dumps(this_file_cov)

    # Write coverage reports
    report = generate_report(coverages, basedir)
    logger.debug('Coverage report: {}'.format(report))
    
    logger.info('Writing coverage report to {}'.format(os.path.abspath(report_filename)))
    with open(report_filename, 'w') as f:
        f.write(report)

def restore(path):
    backups = glob.glob('{}/**/*.qoverage.bkp'.format(path), recursive=True)
    for backup in backups:
        os.rename(backup, backup.replace('.qoverage.bkp', ''))
    dbs = glob.glob('{}/**/*.qoverage.js'.format(path), recursive=True)
    for db in dbs:
        os.remove(db)
    intermediates = glob.glob('{}/**/*.qoverage.pre'.format(path), recursive=True)
    for intermediate in intermediates:
        os.remove(intermediate)

def main():
    try:
        QOVERAGE_LOGLEVEL = os.environ.get('QOVERAGE_LOGLEVEL', 'INFO').upper()
        logging.basicConfig(
            level=QOVERAGE_LOGLEVEL,
            format='[%(name)s] [%(levelname)s] %(message)s'
        )
        logger = logging.getLogger('main')

        parser = argparse.ArgumentParser(
            prog="qoverage",
            description="Code coverage for QML"
        )
        subparsers = parser.add_subparsers(help='sub-command help', dest='command')

        instrument_parser = subparsers.add_parser('instrument', help='Instrument QML files for code coverage')
        instrument_parser.add_argument('-g', '--glob', action='append', help='Add QML files to instrument. Can be used multiple times. Glob wildcards are supported. Default is ./**/*.qml')
        instrument_parser.add_argument('-b', '--glob-base', help='When generating into another directory, this is the path relative to which the globs are interpreted for deterimining the output subdirectory.')
        instrument_parser.add_argument('-q', '--qmldom', help='Path to the qmldom executable. Optional. If not specified, qoverage will try to find it automatically.')
        instrument_parser.add_argument('-i', '--in-place', action='store_true', help='Overwrite the QML files with the annotated versions.')
        instrument_parser.add_argument('-o', '--output-path', help='Path to the output directory. Instrumented files will be stored here in relative paths to the search path.')
        instrument_parser.add_argument('-s', '--store-intermediates', action='store_true', help='Store intermediate files in the output directory. This includes the pre-annotated QML files. This is useful for debugging.')
        instrument_parser.add_argument('-d', '--debug-code', action='store_true', help='Inject additional debug code which is useful for validating the instrumentation.')
        instrument_parser.add_argument('-n', '--no-backups', action='store_true', help='If running in-place instrumentation, usually qml files are backed up to .qoverage.bkp files. This flag disables that behavior.')

        restore_parser = subparsers.add_parser('restore', help='Restore QML files backed up during in-place instrumentation.')
        restore_parser.add_argument('-p', '--path', help='Path to the directory containing the instrumented files. Default is ./')

        collect_parser = subparsers.add_parser('collect', help='Collect code coverage results into a report. Either use -f/--file for parsing a file, or add a separate command on the end with -- <CMD> to run a command and parse directly.')
        collect_parser.add_argument('-r', '--report', default='coverage.xml', help='Path to the output coverage report file. Default is ./coverage.xml')
        collect_parser.add_argument('-b', '--base' , default=os.path.abspath('.'), help='Base path for the coverage report, with respect to which the relative paths in the report are determined.')
        collect_parser.add_argument('-f', '--file', help='Path to a file containing stdout from the instrumented QML application. The file will be parsed for coverage results.')

        my_args = sys.argv[1:]
        remainder = None
        if '--' in my_args:
            separator_index = my_args.index('--')
            remainder = my_args[separator_index+1:]
            my_args = my_args[:separator_index]

        args = parser.parse_args(my_args)

        if args.command == 'instrument':
            if remainder:
                logger.error('The instrument command does not take any additional arguments with a -- separator.')
                exit(1)
            instrument(args, logger, debug=args.debug_code)
            return
        elif args.command == 'collect':
            collect(args.file, remainder, args.base, args.report, logger)
            return
        elif args.command == 'restore':
            if remainder:
                logger.error('The restore command does not take any additional arguments with a -- separator.')
                exit(1)
            if not args.path:
                args.path = '.'
            restore(args.path)
            return
        
    except Exception as e:
        logger.error("Exception: " + str(e) + "\n" + traceback.format_exc())
        exit()