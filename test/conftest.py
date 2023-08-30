import subprocess

def pytest_exception_interact(node, call, report):
    if report.failed \
        and hasattr(node, 'open_diff_tool') and node.open_diff_tool \
        and hasattr(node, 'resultfile') and node.resultfile \
        and hasattr(node, 'referencefile') and node.referencefile:

        subprocess.Popen([node.open_diff_tool, node.resultfile, node.referencefile])