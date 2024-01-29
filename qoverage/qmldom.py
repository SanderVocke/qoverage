from .find_qmldom import find_qmldom
import logging
import subprocess
import xml.dom.minidom
import tempfile
import re

logger = logging.getLogger('qmldom')

def fix_string_literals(ast):
    n_fixes = 0
    def do_replace(find, replace):
        nonlocal ast, n_fixes
        match = re.search(find, ast)
        new_ast, n = re.subn(find, replace, ast)
        ast = new_ast
        logger.debug(n)
        n_fixes += n
        if n > 0:
            do_replace(find, replace)
    
    do_replace(r'(.*<StringLiteral.*value="[^"]*)\\"', r'\1&quot;')
    do_replace(r'(.*<StringLiteral.*value="[^"]*)\'', r'\1&apos;')
    do_replace(r'(.*<StringLiteral.*value="[^"]*)<', r'\1&lt;')
    do_replace(r'(.*<StringLiteral.*value="[^"]*)>', r'\1&gt;')
    do_replace(r'(.*<StringLiteral.*value="[^"]*)&(?!quot;|amp;|lt;|gt;|apos;)', r'\1&amp;')

    logger.debug('Fixed {} occurrences of illegal escapes in string literals (QTBUG116618)'.format(n_fixes))

    return ast
    

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
    
    def ast_dom(self, contents) -> (xml.dom.minidom.Document, ast):
        try:
            ast = self.ast(contents)
            ast = fix_string_literals(ast)

            try:
                return (xml.dom.minidom.parseString(ast), ast)
            except Exception as e:
                logger.error('Failed to parse QMLDom XML: {}'.format(e))
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xml') as f:
                    f.write(ast)
                logger.error('XML file saved to: {} for inspection'.format(f.name))
                return (None, ast)
        except Exception as e:
            logger.error('Failed generate QMLDom XML: {}'.format(e))
