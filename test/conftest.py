import subprocess

results_dir = None
references_dir = None
diff_tool = None

def pytest_exception_interact(node, call, report):
    global results_dir
    global references_dir
    global diff_tool

    if report.failed \
        and hasattr(node, 'open_diff_tool') and node.open_diff_tool \
        and hasattr(node, 'resultfile') and node.resultfile \
        and hasattr(node, 'referencefile') and node.referencefile:

        results_dir = node.resultsdir
        references_dir = node.referencesdir
        diff_tool = node.open_diff_tool

def pytest_unconfigure(config):
    global results_dir
    global references_dir
    global diff_tool

    if results_dir and references_dir and diff_tool:
        subprocess.Popen([diff_tool, results_dir, references_dir])