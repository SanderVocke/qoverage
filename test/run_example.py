#!/usr/bin/env python3

import os
import subprocess
import tempfile
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))
example = sys.argv[1]

QOVERAGE = os.environ.get("QOVERAGE", f"python {script_dir}/../qoverage.py")
QML = os.environ.get("QML", "qml")
output_dir = tempfile.mkdtemp()

print(f"Using qoverage command: {QOVERAGE}")
print(f"Using qml command: {QML}")
print(f"Script dir: {script_dir}")
print(f"Working dir: {os.getcwd()}")

# Instrument
command = f"{QOVERAGE} instrument --store-intermediates --debug-code --path {script_dir}/examples/{example} --output-path {output_dir}"
print(f"Instrumenting:\n  -> {command}")
subprocess.run(command, shell=True, check=True)

# Run
command = f"timeout 3s {QML} {output_dir}/main.qml 2>&1 | tee {output_dir}/run.log"
print(f"Running:\n  -> {command}")
subprocess.run(command, shell=True, check=True)

# Report
command = f"{QOVERAGE} collect --report {output_dir}/report.xml --files-path {output_dir} --input {output_dir}/run.log"
print(f"Reporting:\n  -> {command}")
subprocess.run(command, shell=True, check=True)