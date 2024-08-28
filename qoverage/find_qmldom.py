import glob
import os
import logging
import subprocess

logger = logging.getLogger('find_qmldom')
script_dir = os.path.dirname(os.path.realpath(__file__))

def find_qmldom() -> str:
    """Searches for and returns the path to a suitable qmldom executable.
    
    Args:
        None
    
    Returns:
        str: The path to the qmldom executable if found, None otherwise.
    """
    
    def glob_candidates(path: str):
        """Find executable qmldom files within a given directory and its subdirectories.
        
        Args:
            path (str): The root directory path to search for qmldom files.
        
        Returns:
            list: A list of paths to executable qmldom files found in the specified directory and its subdirectories.
        """
        
        return [e for e in glob.glob("{}/**/qmldom".format(path), recursive=True) if os.access(path, os.X_OK)]

    candidates_per_path = [glob_candidates(path) for path in [
        '{}/bundled_qmldom'.format(script_dir),
        '/usr/lib',
        '/usr/local/lib',
        '/usr/bin',
        '/usr/local/bin'
    ]]
    # flatten
    candidates = [c for sublist in candidates_per_path for c in sublist]

    if len(candidates) == 0:
        return None
    logger.debug('qmldom candidates: {}'.format(candidates))
    
    for candidate in candidates:
        # Try to run it, it may be e.g. for a different architecture
        try:
            subprocess.check_output([candidate, '--version'], stderr=subprocess.DEVNULL)
            return candidate
        except Exception as e:
            logger.debug('qmldom candidate {} failed to run: {}. Trying next candidate.'.format(candidate, e))
            continue
    
    logger.error('Did not find a suitable qmldom executable.')