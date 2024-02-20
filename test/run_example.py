#!/usr/bin/env python3

import os
import subprocess
import tempfile
import sys
import glob

script_dir = os.path.dirname(os.path.realpath(__file__))
example = sys.argv[1]

QOVERAGE = os.environ.get("QOVERAGE", f"python {script_dir}/../qoverage.py")
QML = os.environ.get("QML", "qml")
QMLTESTRUNNER = os.environ.get("QMLTESTRUNNER", "qmltestrunner")
DUMP_RUN_LOG = os.environ.get("DUMP_RUN_LOG", "0") != "0"
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", tempfile.mkdtemp())
REPORT_XML = os.environ.get("REPORT_XML", f"{OUTPUT_DIR}/report.xml")

print(f"Using qoverage command: {QOVERAGE}")
print(f"Using qml command: {QML}")
print(f"Using qmltestrunner command: {QMLTESTRUNNER}")
print(f"Script dir: {script_dir}")
print(f"Working dir: {os.getcwd()}")
print(f"Output dir: {OUTPUT_DIR}")

def run_and_check(step, command, maybe_write_log=None):
    print(f"{step}:\n  -> {command}")
    r = subprocess.run(command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    output = r.stdout.decode()
    if r.returncode != 0:
        print(f"{step} failed.")
    if DUMP_RUN_LOG or r.returncode != 0:
        print(f"{step} log:")
        print(output)
    if r.returncode != 0:
        exit(r.returncode)
    if maybe_write_log:
        with open(maybe_write_log, "w") as f:
            f.write(output)

run_and_check('Instrumentation', f"{QOVERAGE} instrument --store-intermediates --debug-code --path {script_dir}/examples/{example} --output-path {OUTPUT_DIR}")

if os.path.exists(os.path.join(OUTPUT_DIR, 'main.qml')):
    run_and_check('Run', f"timeout 3s {QML} --verbose {OUTPUT_DIR}/main.qml", f"{OUTPUT_DIR}/run.log")
elif len(glob.glob(os.path.join(OUTPUT_DIR, 'tst_*.qml'))) > 0:
    run_and_check('Run', f"timeout 3s {QMLTESTRUNNER} -input {OUTPUT_DIR}", f"{OUTPUT_DIR}/run.log")

run_and_check('Collect', f"{QOVERAGE} collect --files-path {OUTPUT_DIR} --input {OUTPUT_DIR}/run.log --report {REPORT_XML}")