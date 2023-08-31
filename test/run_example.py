#!/usr/bin/env python3

import os
import subprocess
import tempfile
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))
example = sys.argv[1]

QOVERAGE = os.environ.get("QOVERAGE", f"python {script_dir}/../qoverage.py")
QML = os.environ.get("QML", "qml")
DUMP_RUN_LOG = os.environ.get("DUMP_RUN_LOG", "0") != "0"
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", tempfile.mkdtemp())

print(f"Using qoverage command: {QOVERAGE}")
print(f"Using qml command: {QML}")
print(f"Script dir: {script_dir}")
print(f"Working dir: {os.getcwd()}")

# Instrument
command = f"{QOVERAGE} instrument --store-intermediates --debug-code --path {script_dir}/examples/{example} --output-path {OUTPUT_DIR} 2>&1 | tee {OUTPUT_DIR}/instrument.log"
print(f"Instrumenting:\n  -> {command}")
subprocess.run(command, shell=True, check=True)
if DUMP_RUN_LOG:
    try:
        with open(f"{OUTPUT_DIR}/instrument.log", 'r') as f:
            print("Instrument log:")
            print(f.read())
    except Exception:
        print("No instrument log was found.")

# Run
command = f"timeout 3s {QML} --verbose {OUTPUT_DIR}/main.qml 2>&1 | tee {OUTPUT_DIR}/run.log"
print(f"Running:\n  -> {command}")
subprocess.run(command, shell=True, check=True)
if DUMP_RUN_LOG:
    try:
        with open(f"{OUTPUT_DIR}/run.log", 'r') as f:
            print("Run log:")
            print(f.read())
    except Exception:
        print("No run log was found.")

# Report
command = f"{QOVERAGE} collect --report {OUTPUT_DIR}/report.xml --files-path {OUTPUT_DIR} --input {OUTPUT_DIR}/run.log 2>&1 | tee {OUTPUT_DIR}/report.log"
print(f"Reporting:\n  -> {command}")
subprocess.run(command, shell=True, check=True)
if DUMP_RUN_LOG:
    try:
        with open(f"{OUTPUT_DIR}/report.log", 'r') as f:
            print("Reporting log:")
            print(f.read())
    except Exception:
        print("No reporting log was found.")