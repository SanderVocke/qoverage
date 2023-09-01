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

output_base_dir = os.environ.get("OUTPUT_DIR", tempfile.mkdtemp())

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
        report_xml = None

        try:
            env = os.environ.copy()
            env['OUTPUT_DIR'] = output_base_dir + '/' + example
            report_xml = env['OUTPUT_DIR'] + '/report.xml'
            env["REPORT_XML"] = report_xml
            os.makedirs(env['OUTPUT_DIR'], exist_ok=True)
            output = subprocess.check_output([
                    PYTHON,
                    f"{script_dir}/run_example.py",
                    example
                ],
                env=env,
                stderr=subprocess.STDOUT
            ).decode('utf-8')
        except subprocess.CalledProcessError as e:
            print(e.output.decode('utf-8'))
            raise e
        print(output)
        dom = None
        with open(report_xml, 'r') as f:
            dom = xml.dom.minidom.parseString(f.read())
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
            cov_marker_default_offset = None

            with open(os.path.join(script_dir, 'examples', example, file), 'r') as f:
                reference = f.read()
                first_line = reference.split('\n')[0]
                match = re.search(r'//COV:([^\s]+)', first_line)
                if match:
                    cov_marker_default_offset = match.start()

            for idx,line_results in enumerate(results):
                result = 'null' if line_results['coverage'] == None else str(line_results['coverage'])
                match = re.match(r'(.*//COV:).*', line_results['reference_line'])
                if match:
                    # Line already has a coverage marker in the reference, replace number by our result
                    # for a nice side-by-side diff
                    compare_to += re.sub(r'(.*//COV:).*', r'\g<1>' + result, line_results['reference_line'])
                elif cov_marker_default_offset != None and len(line_results['reference_line'].rstrip()) < cov_marker_default_offset:
                    # Reference line has no coverage marker, add one at the same offset as line 1
                    ref = line_results['reference_line'].rstrip()
                    n_spaces = cov_marker_default_offset - len(ref)
                    compare_to += ref + ' ' * n_spaces + '//COV:' + result + '\n'
                else:
                    # No coverage marker on a long line, put it at the end
                    compare_to += line_results['reference_line'].rstrip() + ' //COV:' + result + '\n'
                    
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

            assert compare_to == reference, 'Coverage comparison failed. Output stored at {}, references stored/linked at {}, generated report at {}. Use OPEN_DIFF_TOOL=tool to open a diff view automatically.'.format(all_results_dir, all_references_dir, report_xml)

