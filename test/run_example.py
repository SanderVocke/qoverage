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
print(f"Output dir: {OUTPUT_DIR}")

# Instrument
command = f"{QOVERAGE} instrument --store-intermediates --debug-code --path {script_dir}/examples/{example} --output-path {OUTPUT_DIR}"
print(f"Instrumenting:\n  -> {command}")
r = subprocess.run(command, shell=True, check=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
if DUMP_RUN_LOG:
    print("Instrument log:")
    print(r.stdout.decode())

# Run
command = f"timeout 3s {QML} --verbose {OUTPUT_DIR}/main.qml"
print(f"Running:\n  -> {command}")
r = subprocess.run(command, shell=True, check=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
if DUMP_RUN_LOG:
    print("Run log:")
    print(r.stdout.decode())
# Write the run log for the next step
with open(f"{OUTPUT_DIR}/run.log", "w") as f:
    f.write(r.stdout.decode())

# Report
command = f"{QOVERAGE} collect --report {OUTPUT_DIR}/report.xml --files-path {OUTPUT_DIR} --input {OUTPUT_DIR}/run.log"
print(f"Reporting:\n  -> {command}")
r = subprocess.run(command, shell=True, check=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
if DUMP_RUN_LOG:
    print("Collect log:")
    print(r.stdout.decode())