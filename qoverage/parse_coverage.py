import logging
import re
import copy

logger = logging.getLogger('parse')

def parse_coverage(lines, aggregated_data, debug=False):
    result = copy.deepcopy(aggregated_data)
    for line in lines:
        match = re.match(r'.*<QOVERAGERESULT file="(.*)">(.*)<\/QOVERAGERESULT>.*', line)
        if match:
            file = match.group(1)
            coverage = match.group(2)
            if file in aggregated_data:
                logger.error('Received coverage for {} twice. This should not happen. Discarding exsting data.'.format(file))
            result[file] = coverage
            logger.info('Collected coverage for {}'.format(file))
    return result