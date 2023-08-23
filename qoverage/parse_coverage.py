import logging
import re
import copy
import os

logger = logging.getLogger('parse')

def parse_coverage(lines, aggregated_data, base_dir, debug=False):
    result = copy.deepcopy(aggregated_data)
    for line in lines:
        match = re.match(r'.*<QOVERAGERESULT file="(.*)">(.*)<\/QOVERAGERESULT>.*', line)
        if match:
            file = os.path.relpath(match.group(1), base_dir)
            coverage = match.group(2)
            if file in aggregated_data:
                logger.error('Received coverage for {} twice. This should not happen. Discarding exsting data.'.format(file))
            result[file] = coverage
            logger.info('Collected coverage for {}'.format(file))
    return result