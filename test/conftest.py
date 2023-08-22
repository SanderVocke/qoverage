import subprocess

def pytest_exception_interact(node, call, report):
    if report.failed \
        and node.open_diff_tool \
        and node.resultfile \
        and node.referencefile:

        subprocess.Popen([node.open_diff_tool, node.resultfile, node.referencefile])