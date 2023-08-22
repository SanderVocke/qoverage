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

@pytest.mark.parametrize("example_name", all_examples)
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
            basename = package.getAttribute('name').replace('.', '/')
            for file in package.getElementsByTagName('class'):

                filename = os.path.relpath(file.getAttribute('filename'), basename)

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
                    match = re.match(r'.*//\s*COV:([^\s]+)', reference_lines[idx])
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
                compare_to += re.sub(r'(.*// COV:).*', r'\g<1>' + result, line_results['reference_line'])
            
            temp_dir = None
            if compare_to != reference:
                temp_dir = tempfile.mkdtemp(prefix=example + '_')
                with open(os.path.join(temp_dir, 'reference.qml'), 'w') as f:
                    f.write(reference)
                with open(os.path.join(temp_dir, 'result.qml'), 'w') as f:
                    f.write(compare_to)

            self.request.node.resultfile = os.path.join(temp_dir, 'result.qml')
            self.request.node.referencefile = os.path.join(temp_dir, 'reference.qml')

            assert compare_to == reference, 'Coverage comparison failed. Output stored at {}, generated report at {}. Use OPEN_DIFF_TOOL=tool to open a diff view automatically.'.format(temp_dir, xmlfile)

