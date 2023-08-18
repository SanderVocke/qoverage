import pytest
import os
import subprocess
import xml.dom.minidom
import re
import tempfile
import glob

script_dir = os.path.dirname(os.path.realpath(__file__))

PYTHON = os.environ.get("PYTHON", "python")

all_examples = [os.path.basename(g) for g in glob.glob(os.path.join(script_dir, 'examples', '*'))]

@pytest.mark.parametrize("example_name", all_examples)
class TestClass:
    def test_example(self, example_name):
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

                ori_qml = os.path.join(script_dir, 'examples', example, filename)
                ori_lines = None
                
                with open(ori_qml, 'r') as f:
                    ori_lines = f.readlines()
                
                coverage = [ None ] * len(ori_lines)
                file_results = [ None ] * len(ori_lines)

                for line in file.getElementsByTagName('line'):
                    nr = int(line.getAttribute('number'))
                    coverage[nr-1] = int(line.getAttribute('hits'))
                
                for idx in range(len(ori_lines)):
                    file_results[idx] = {}
                    file_results[idx]['ori_line'] = ori_lines[idx]
                    file_results[idx]['coverage'] = coverage[idx]
                    file_results[idx]['line_idx'] = idx + 1
                    match = re.match(r'.*//\s*COV:([^\s]+)', ori_lines[idx])
                    if match:
                        expect_str = match.group(1)
                        if expect_str != 'null':
                            file_results[idx]['expect'] = int(expect_str)
                        else:
                            file_results[idx]['expect'] = None

                results[filename] = file_results


        for file, results in results.items():
            compare_to = ''
            ori = None

            with open(os.path.join(script_dir, 'examples', example, file), 'r') as f:
                ori = f.read()

            for idx,line_results in enumerate(results):
                result = 'null' if line_results['coverage'] == None else str(line_results['coverage'])
                compare_to += re.sub(r'(.*// COV:).*', r'\g<1>' + result, line_results['ori_line'])
            
            temp_dir = None
            if compare_to != ori:
                temp_dir = tempfile.mkdtemp()
                with open(os.path.join(temp_dir, 'ori.qml'), 'w') as f:
                    f.write(ori)
                with open(os.path.join(temp_dir, 'result.qml'), 'w') as f:
                    f.write(compare_to)
            assert compare_to == ori, 'Coverage comparison failed. Output stored at {}, generated report at {}.'.format(temp_dir, xmlfile)

        # for file,results in results.items():
        #     for line_results in results:
        #         assert line_results['coverage'] == line_results['expect'], \
        #             'Fail on line {} of {}. Expected {}, got {}'.format(
        #                 line_results['line_idx'],
        #                 file,
        #                 line_results['expect'],
        #                 line_results['coverage']
        #             )

