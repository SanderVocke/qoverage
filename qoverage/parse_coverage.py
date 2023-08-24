import logging
import re
import copy
import os

logger = logging.getLogger('parse')

def parse_coverage(lines, filename_transform_fn):
    result = {}
    for line in lines:
        match = re.match(r'.*<QOVERAGERESULT file="(.*)">(.*)<\/QOVERAGERESULT>.*', line)
        if match:
            ori_file = match.group(1)
            file = filename_transform_fn(ori_file)
            if not os.path.exists(file):
                if file == ori_file:
                    logger.warning('Received coverage for {} but file does not exist. Skipping. If your instrumented files have moved, please use --strip-paths-expr to find them.'.format(file))
                else:
                    logger.warning('Received coverage for {} (original reported name: {}) but file does not exist. Skipping. If your instrumented files have moved, please check your --strip-paths-expr.'.format(file, ori_file))
                continue
            coverage = match.group(2)
            if file in result:
                logger.warning('Received coverage for {} twice. This should probably not happen - please check your coverage dump implementation. Discarding exsting data.'.format(file))
            result[file] = coverage
            logger.info('Collected coverage for {}'.format(file))
    return result