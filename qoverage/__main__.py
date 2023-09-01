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
    globs = args.glob if args.glob else []
    if args.path and not args.glob_base:
        args.glob_base = args.path[0]
    globs.extend(['{}/**/*.qml'.format(p) for p in args.path] if args.path else [])
    globs.extend(['{}/**/*.js'.format(p) for p in args.path] if args.path else [])
    globs.extend(['{}/**/*.mjs'.format(p) for p in args.path] if args.path else [])
    if not globs or len(globs) == 0:
        globs = ['./**/*.qml']
    def do_glob(path):
        logger.debug('Globbing: {}'.format(path))
        return glob.glob(path, recursive=True)
    
    qml_files = [do_glob(g) for g in globs]
    # flatten
    qml_files = [item for sublist in qml_files for item in sublist]
    if len(qml_files) == 0:
        logger.error('No QML files found. Please provide (a) globbing path(s) to the QML files with --path or --glob.')
        exit(1)
    logger.debug('Files to instrument: {}'.format(qml_files))
    logger.info('Found {} QML files'.format(
        len(qml_files)
        ))
    
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
        backup = '{}.qoverage.bkp'.format(qml_file)
        if os.path.exists(backup):
            logger.info('Backup file already exists. Instrumenting from the backup: {}'.format(qml_file))
            qml_file = backup
            continue
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
            os.makedirs(os.path.dirname(out_file), exist_ok=True)
        try:
            db_js_filename = out_file + '.qoverage.js'
            # Touch the file so that it will be detected during collection, even if annotation
            # fails
            with open(db_js_filename, 'w') as f:
                pass
            pre_annotated = pre_annotate(contents, qmldom, debug=debug)
            annotated,runtime_db_js = final_annotate(pre_annotated, os.path.basename(db_js_filename), debug=debug)
            logger.debug('Writing instrumented file to: {}'.format(out_file))
            with open(out_file, 'w') as f:
                f.write(annotated)
            logger.debug('Writing instrumentation companion JS library to: {}'.format(db_js_filename))
            with open(db_js_filename, 'w') as f:
                f.write(runtime_db_js)
            if args.store_intermediates:
                logger.debug('Writing intermediate (pre-annotated) file to: {}'.format(out_file + '.qoverage.pre'))
                with open(out_file + '.qoverage.pre', 'w') as f:
                    f.write(pre_annotated)
        except Exception as e:
            logger.error('Failed to instrument {}: {}. Skipping.'.format(qml_file, e))
            logger.debug(traceback.format_exc())
            continue
    
def collect(input, maybe_cmd, files_path, report, maybe_strip_paths_expr, maybe_prefix, logger):
    if not maybe_prefix:
        maybe_prefix = ''
    
    if maybe_cmd and input:
        raise Exception("Both a filename and a command were passed. Parsing can be done either on a file or on the output of a command, but not both.")
    if not maybe_cmd and not input:
        raise Exception("Neither a filename nor a command were passed. Parsing can be done either on a file or on the output of a command.")

    lines = []
    if input:
        logger.info('Parsing: {}'.format(input))
        with open(input, 'r') as f:
            lines = f.readlines()
    elif maybe_cmd:
        logger.info('Running: {}'.format(' '.join(maybe_cmd)))
        p = subprocess.Popen(maybe_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout:
            line = line.decode('utf-8')
            print(line, end='')
            lines.append(line)
        p.wait()

    norm_files_path = os.path.normpath(os.path.abspath(files_path)) + '/'
    
    # Collect coverage data from the logs/dump.
    def filename_transform_to_reported(f):
        # Transform filenames from the log data to the files as will be reported.
        rval = f
        if maybe_strip_paths_expr:
            rval = re.sub(maybe_strip_paths_expr, norm_files_path, rval)
        rval = os.path.normpath(os.path.abspath(rval))
        return maybe_prefix + rval.replace(norm_files_path, '')
    
    coverages = parse_coverage(lines, filename_transform_to_reported)

    # Put 0 coverage data for files that were not collected
    instrumentation_js_libs = [os.path.normpath(os.path.abspath(g)) for g in glob.glob('{}/**/*.qoverage.js'.format(norm_files_path), recursive=True)]
    for instrumentation_js in instrumentation_js_libs:
        tracked_file = instrumentation_js.replace('.qoverage.js', '')
        name_in_report = maybe_prefix + tracked_file.replace(norm_files_path, '')
        if not name_in_report in coverages:
            logger.warning('File was never loaded: {}. Inserting 0 coverage.'.format(name_in_report))
            
            n_lines = None
            include_lines = None

            try:
                # Parse the instrumentation JS to find some info such as the amount of lines and
                # which lines are eligible for tracking. Use that to create a 0 coverage report.
                with open(instrumentation_js, 'r') as f:
                    contents = f.read()

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
            except Exception:
                # Could not parse instrumentation lib. Assume all lines matter.
                logger.warning('  -> Source was not correctly instrumented. Assuming all lines are eligible for tracking.')
                with open(tracked_file, 'r') as f:
                    n_lines = len(f.readlines())
                    include_lines = list(range(n_lines))

            this_file_cov = [None] * n_lines
            for line in include_lines:
                this_file_cov[line] = 0
                
            coverages[name_in_report] = json.dumps(this_file_cov)

    # Write coverage reports
    report_contents = generate_report(coverages)
    logger.debug('Coverage report: {}'.format(report_contents))
    
    logger.info('Writing coverage report to {}'.format(os.path.abspath(report)))
    with open(report, 'w') as f:
        f.write(report_contents)

def restore(path, logger):
    backups = glob.glob('{}/**/*.qoverage.bkp'.format(path), recursive=True)
    logger.info("Found {} backups, restoring.".format(len(backups)))
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
        parser = argparse.ArgumentParser(
            prog="qoverage",
            description="Code coverage for QML"
        )
        parser.add_argument('-v', '--verbose', action='store_true', help='Print debug messages')
        
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
        instrument_parser.add_argument('-p', '--path', action='append', help='Add QML file search path. Equivalent to --glob <path>/**/*.qml. Can be used multiple times.')
        instrument_parser.add_argument('-v', '--verbose', action='store_true', help='Print debug messages')

        restore_parser = subparsers.add_parser('restore', help='Restore QML files backed up during in-place instrumentation.')
        restore_parser.add_argument('-p', '--path', help='Path to the directory containing the instrumented files. Default is ./')
        restore_parser.add_argument('-v', '--verbose', action='store_true', help='Print debug messages')

        collect_parser = subparsers.add_parser('collect', help='Collect code coverage results into a report. Either use -f/--file for parsing a file, or add a separate command on the end with -- <CMD> to run a command and parse directly.')
        collect_parser.add_argument('-f', '--files-path', help='Path to the directory containing the instrumented files. This path will be scanned for instrumented files which make up the report. Filenames in the report are also reported relative to this path.')
        collect_parser.add_argument('-r', '--report', default='coverage.xml', help='Path to the output coverage report file. Default is ./coverage.xml')
        collect_parser.add_argument('-v', '--verbose', action='store_true', help='Print debug messages')
        collect_parser.add_argument('-s', '--strip-paths-expr', help='Regular expression which is applied to the paths in the parsed log file. The matching part is stripped from the path, then replaced by --files-path in order to find the actual files. Useful if --files-path does not match the original location where data was collected (e.g. when Qoverage collect runs in a container). Note that the resulting path should lead to files that actually exist on the filesystem.')
        collect_parser.add_argument('-i', '--input', help='The input file containing dumped qoverage information (e.g. a stdout log). The file will be parsed for coverage results.')
        collect_parser.add_argument('-p', '--report-prefix', help='Final prefix added to the filenames in the report. Affects reporting only - files do not need to exist on the filesystem under this path.')

        my_args = sys.argv[1:]
        maybe_command = None
        if '--' in my_args:
            separator_index = my_args.index('--')
            maybe_command = my_args[separator_index+1:]
            my_args = my_args[:separator_index]

        args = parser.parse_args(my_args)
        
        QOVERAGE_LOGLEVEL = os.environ.get('QOVERAGE_LOGLEVEL', 'INFO').upper()
        if args.verbose:
            QOVERAGE_LOGLEVEL = 'DEBUG'
        logging.basicConfig(
            level=QOVERAGE_LOGLEVEL,
            format='[%(name)s] [%(levelname)s] %(message)s'
        )
        logger = logging.getLogger('main')

        if args.command == 'instrument':
            if maybe_command:
                logger.error('The instrument command does not take any additional arguments with a -- separator.')
                exit(1)
            instrument(args, logger, debug=args.debug_code)
            return
        elif args.command == 'collect':
            collect(args.input, maybe_command, args.files_path, args.report, args.strip_paths_expr, args.report_prefix, logger)
            return
        elif args.command == 'restore':
            if maybe_command:
                logger.error('The restore command does not take any additional arguments with a -- separator.')
                exit(1)
            if not args.path:
                args.path = '.'
            restore(args.path, logger)
            return
        
    except Exception as e:
        raise Exception(str(e) + "\n" + traceback.format_exc())

if __name__ == '__main__':
    import coverage
    with open('/tmp/cov.txt', 'a') as f:
        f.write('qoverage, {} {} {}\n'.format(os.environ.get('COVERAGE_PROCESS_START'), os.environ.get('COVERAGE_RUN'), os.environ.get("COVERAGE_FILE")))
    main()