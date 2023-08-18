from .find_qmldom import find_qmldom
import logging
import subprocess
import xml.dom.minidom
import tempfile

logger = logging.getLogger('qmldom')

class QMLDom:
    def __init__(self, qmldom_path=None) -> None:
        self.qmldom = qmldom_path or find_qmldom()

        logger.debug('Using qmldom: {}'.format(self.qmldom))
        logger.debug('qmldom version: {}'.format(self.qmldom_version()))
    
    def qmldom_version(self) -> str:
        return subprocess.check_output([self.qmldom, '--version']).decode('utf-8').strip()
    
    def ast(self, contents) -> str:
        with tempfile.NamedTemporaryFile(mode='w', delete=True, suffix='.qml') as f:
            f.write(contents)
            f.flush()
            return subprocess.check_output([self.qmldom, '--dump-ast', f.name], stderr=subprocess.DEVNULL).decode('utf-8')
    
    def ast_dom(self, contents) -> xml.dom.minidom.Document:
        return xml.dom.minidom.parseString(self.ast(contents))
