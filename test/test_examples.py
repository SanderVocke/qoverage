#!/bin/python

import pytest
import os
import subprocess
import xml.dom.minidom
import re
import tempfile
import glob

script_dir = os.path.dirname(os.path.realpath(__file__))

PYTHON = os.environ.get("PYTHON", "python")
OPEN_DIFF_TOOL = os.environ.get("OPEN_DIFF_TOOL", None)

all_examples = [os.path.basename(g) for g in glob.glob(os.path.join(script_dir, 'examples', '*'))]
all_examples_params = [
    pytest.param(e, marks=pytest.mark.xfail()) if re.search(r'.*notworking.*', e) else e for e in all_examples
]

all_results_dir = None
all_references_dir = None

@pytest.mark.parametrize("example_name", all_examples_params)
class TestClass:

    def test_example(self, example_name, request):
        self.example_name = example_name
        self.request = request
        self.request.node.open_diff_tool = OPEN_DIFF_TOOL
        print(self)
        print(example_name)
        print(request)
        self.run(example_name)
        
    def run(self, example):
        results = {}

        try:
            output = subprocess.check_output([PYTHON, f"{script_dir}/run_example.py", example], stderr=subprocess.STDOUT).decode('utf-8')
        except subprocess.CalledProcessError as e:
            print(e.output.decode('utf-8'))
            raise e
        print(output)
        dom = None
        xmlfile = None
        for line in output.split('\n'):
            match = re.match(r'.*Writing coverage report to (.*\.xml).*', line)
            if match:
                xmlfile = match.group(1)
                with open(xmlfile, 'r') as f:
                    dom = xml.dom.minidom.parseString(f.read())
                    break
        if not dom:
            raise Exception('Could not find and/or parse coverage report')
        
        for package in dom.getElementsByTagName('package'):
            for file in package.getElementsByTagName('class'):
                filename = file.getAttribute('filename')

                reference_qml = os.path.join(script_dir, 'examples', example, filename)
                reference_lines = None
                
                with open(reference_qml, 'r') as f:
                    reference_lines = f.readlines()
                
                coverage = [ None ] * len(reference_lines)
                file_results = [ None ] * len(reference_lines)

                for line in file.getElementsByTagName('line'):
                    nr = int(line.getAttribute('number'))
                    coverage[nr-1] = int(line.getAttribute('hits'))
                
                for idx in range(len(reference_lines)):
                    file_results[idx] = {}
                    file_results[idx]['reference_line'] = reference_lines[idx]
                    file_results[idx]['coverage'] = coverage[idx]
                    file_results[idx]['line_idx'] = idx + 1
                    match = re.match(r'.*//COV:([^\s]+)', reference_lines[idx])
                    if match:
                        expect_str = match.group(1)
                        if expect_str != 'null':
                            file_results[idx]['expect'] = int(expect_str)
                        else:
                            file_results[idx]['expect'] = None

                results[filename] = file_results


        for file, results in results.items():
            compare_to = ''
            reference = None

            with open(os.path.join(script_dir, 'examples', example, file), 'r') as f:
                reference = f.read()

            for idx,line_results in enumerate(results):
                result = 'null' if line_results['coverage'] == None else str(line_results['coverage'])
                compare_to += re.sub(r'(.*//COV:).*', r'\g<1>' + result, line_results['reference_line'])
            
            if compare_to != reference:
                global all_results_dir
                global all_references_dir
                if all_results_dir == None:
                    temp_dir = tempfile.mkdtemp()
                    all_results_dir = temp_dir + '/results'
                    all_references_dir = temp_dir + '/references'
                resultdir = all_results_dir + '/' + example
                refdir = all_references_dir + '/' + example
                os.makedirs(resultdir, exist_ok=True)
                os.makedirs(refdir, exist_ok=True)
                try:
                    os.symlink(os.path.join(script_dir, 'examples', example, file), os.path.join(refdir, file))
                except Exception:
                    with open(os.path.join(refdir, file), 'w') as f:
                        f.write(reference)
                with open(os.path.join(resultdir, file), 'w') as f:
                    f.write(compare_to)

                # For PyTest hooks
                self.request.node.resultsdir = all_results_dir
                self.request.node.referencesdir = all_references_dir

            assert compare_to == reference, 'Coverage comparison failed. Output stored at {}, generated report at {}. Use OPEN_DIFF_TOOL=tool to open a diff view automatically.'.format(temp_dir, xmlfile)

