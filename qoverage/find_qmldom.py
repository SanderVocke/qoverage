import glob
import os
import logging

logger = logging.getLogger('find_qmldom')
script_dir = os.path.dirname(os.path.realpath(__file__))

def find_qmldom() -> str:
    def glob_candidates(path: str):
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
    return candidates[0]