import subprocess

results_dir = None
references_dir = None
diff_tool = None

def pytest_exception_interact(node, call, report):
    """Handle interaction with an exception during test execution.
    
    Args:
        node (pytest.Item): The test item that raised the exception
        call (pytest.CallInfo): Information about the test function call
        report (pytest.TestReport): The test report object
    
    Returns:
        None: This function does not return anything
    
    """
    global results_dir
    global references_dir
    global diff_tool

    if report.failed \
        and hasattr(node, 'open_diff_tool') and node.open_diff_tool \
        and hasattr(node, 'resultsdir') and node.resultsdir \
        and hasattr(node, 'referencesdir') and node.referencesdir:

        results_dir = node.resultsdir
        references_dir = node.referencesdir
        diff_tool = node.open_diff_tool

def pytest_unconfigure(config):
    """Unconfigures pytest and launches a diff tool to compare results and references.
    
    Args:
        config: The pytest configuration object.
    
    Returns:
        None: This function does not return anything.
    """
    
    global results_dir
    global references_dir
    global diff_tool

    if results_dir and references_dir and diff_tool:
        subprocess.Popen([diff_tool, results_dir, references_dir])