from .find_qmldom import find_qmldom
import logging
import subprocess
import xml.dom.minidom
import tempfile

logger = logging.getLogger('qmldom')

class QMLDom:
    def __init__(self, qmldom_path=None) -> None:
        self.qmldom = qmldom_path or find_qmldom()

        logger.info('Using qmldom: {}'.format(self.qmldom))
        logger.debug('qmldom version: {}'.format(self.qmldom_version()))
    
    def qmldom_version(self) -> str:
        return subprocess.check_output([self.qmldom, '--version']).decode('utf-8').strip()
    
    def ast(self, contents) -> str:
        with tempfile.NamedTemporaryFile(mode='w', delete=True, suffix='.qml') as f:
            try:
                f.write(contents)
                f.flush()
                return subprocess.check_output([self.qmldom, '--dump-ast', f.name], stderr=subprocess.DEVNULL).decode('utf-8')
            except Exception as e:
                logger.error('Failed to parse QML file: {}'.format(e))
                return ''
    
    def ast_dom(self, contents) -> xml.dom.minidom.Document:
        try:
            ast = self.ast(contents)

            # Because of QTBUG-116618. This may be overkill, but haven't had failures with it so far.
            ast = ast.replace(r'\"', '&quot;')

            try:
                return xml.dom.minidom.parseString(ast)
            except Exception as e:
                logger.error('Failed to parse QMLDom XML: {}'.format(e))
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xml') as f:
                    f.write(ast)
                logger.error('XML file saved to: {} for inspection'.format(f.name))
                return None
        except Exception as e:
            logger.error('Failed generate QMLDom XML: {}'.format(e))
