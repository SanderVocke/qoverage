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

# Instrument
command = f"{QOVERAGE} instrument --store-intermediates --debug-code --glob {script_dir}/examples/{example}/**/*.qml --glob-base {script_dir}/examples/{example} --output-path {output_dir}"
print(f"Instrumenting:\n  -> {command}")
subprocess.run(command, shell=True, check=True)

# Run
command = f"{QML} {output_dir}/main.qml &> {output_dir}/run.log"
print(f"Running:\n  -> {command}")
subprocess.run(command, shell=True, check=True)

# Report
command = f"{QOVERAGE} collect --report {output_dir}/report.xml --base {output_dir} --file {output_dir}/run.log"
print(f"Reporting:\n  -> {command}")
subprocess.run(command, shell=True, check=True)