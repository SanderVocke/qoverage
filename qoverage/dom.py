import xml.dom
import xml.dom.minidom
import re
import logging

logger = logging.getLogger('qoverage.dom')

def parse_token_loc(loc: str):
    match = re.match(r'off:(\d+) len:(\d+) l:(\d+) c:(\d+)', loc)
    if match:
        return {
            'offset': int(match.group(1)),
            'length': int(match.group(2)),
            'line': int(match.group(3)),
            'column': int(match.group(4))
        }
    return None

def token_loc(node, attribute):
    token = node.getAttribute(attribute)
    if token:
        return parse_token_loc(token)
    return None

def token_offset(node, token_name_or_names, add_length=False):
    if isinstance (token_name_or_names, list):
        for name in token_name_or_names:
            maybe_result = token_offset(node, name, add_length)
            if (maybe_result != None):
                return maybe_result
    
    loc = token_loc(node, token_name_or_names)
    if loc:
        return (loc['offset'] if not add_length else loc['offset'] + loc['length'])
    return None

def node_is(node, tag_name_or_names):
    def match(name):
        if isinstance(tag_name_or_names, str):
            return name == tag_name_or_names
        elif isinstance(tag_name_or_names, list):
            return name in tag_name_or_names

    return match(node.nodeName)

def node_as(node, tag_name_or_names):
    if node_is(node, tag_name_or_names):
        return node
    return None

def parent_as(node, tag_name_or_names):
    if node.parentNode.nodeName == 'Node':
        return parent_as(node.parentNode, tag_name_or_names)
    return node_as(node.parentNode, tag_name_or_names)

def children_filter_nodes(node):
    def child(c):
        if node_is(c, 'Node'):
            return children_filter_nodes(c)[0]
        elif c.nodeType == xml.dom.Node.ELEMENT_NODE:
            return c
        return None
    
    return [child(c) for c in node.childNodes if child(c)]

# For a given node, return the start offset in characters from the start of the file,
# to the point just before where it is executed/evauated.
# If unknown/not applicable, return None.
def node_eval_start_offset(node):
    def from_attrib(attrib, add_length=False):
        return token_offset(node, attrib)
    
    per_node_type = {
        'BreakStatement': lambda: from_attrib('breakToken'),
        'ExpressionStatement': lambda: node_eval_start_offset(children_filter_nodes(node)[0]),
        'CallExpression': lambda: node_eval_start_offset(children_filter_nodes(node)[0]),
        'BinaryExpression': lambda: node_eval_start_offset(children_filter_nodes(node)[0]),
        'FieldMemberExpression':  lambda: node_eval_start_offset(children_filter_nodes(node)[0]),
        'IdentifierExpression': lambda: from_attrib(['identifierToken', 'identiferToken']),
        'NumericLiteral': lambda: from_attrib('literalToken'),
        'ForStatement': lambda: from_attrib('forToken'),
        'IfStatement': lambda: from_attrib('ifToken'),
        'SwitchStatement': lambda: from_attrib('switchToken'),
        'ReturnStatement': lambda: from_attrib('returnToken'),
        'VariableStatement': lambda: from_attrib('declarationKindToken'),
        'TrueLiteral': lambda: from_attrib('trueToken'),
        'FalseLiteral': lambda: from_attrib('falseToken'),
        'StringLiteral': lambda: from_attrib('literalToken'),
    }

    rval = None
    if node.nodeName in per_node_type:
        rval = per_node_type[node.nodeName]()

    if rval == None:
        logger.debug('No eval start offset found for {} node.'.format(node.nodeName))
    return rval

# For a given node, return the start offset in characters from the start of the file,
# to the point just after where it is executed/evaluated.
# If unknown/not applicable, return None.
def node_eval_end_offset(node):
    def from_attrib(attrib, add_length=False):
        return token_offset(node, attrib, add_length)
    
    per_node_type = {
        'BreakStatement': lambda: from_attrib('breakToken', True),
        'ExpressionStatement': lambda: node_eval_end_offset(children_filter_nodes(node)[-1]),
        'CallExpression': lambda: from_attrib('rparenToken', True),
        'BinaryExpression': lambda: node_eval_end_offset(children_filter_nodes(node)[-1]),
        'FieldMemberExpression':  lambda: from_attrib(['identifierToken', 'identiferToken'], True),
        'IdentifierExpression': lambda: from_attrib(['identifierToken', 'identiferToken'], True),
        'NumericLiteral': lambda: from_attrib('literalToken', True),
        'ReturnStatement': lambda: from_attrib('returnToken', True),
        'VariableStatement': lambda: node_eval_end_offset(children_filter_nodes(node)[-1]),
        'VariableDeclarationList': lambda: node_eval_end_offset(children_filter_nodes(node)[-1]),
        'PatternElement': lambda: node_eval_end_offset(children_filter_nodes(node)[-1]),
        'TrueLiteral': lambda: from_attrib('trueToken', True),
        'FalseLiteral': lambda: from_attrib('falseToken', True),
        'StringLiteral': lambda: from_attrib('literalToken', True),
    }

    rval = None
    if node.nodeName in per_node_type:
        rval = per_node_type[node.nodeName]()

    return rval

# For a given node, if it is a node where simple linear execution can end
# (i.e. a return or conditional), return the offset at which we can insert
# a marker just before linear execution ends.
# If unknown/not applicable, return None.
def maybe_node_linear_execution_end_offset(node):
    def from_attrib(attrib, add_length=False):
        return token_offset(node, attrib)
    
    per_node_type = {
        'BreakStatement': lambda: from_attrib('breakToken'),
        'ForStatement': lambda: from_attrib('forToken'),
        'IfStatement': lambda: from_attrib('ifToken'),
        'SwitchStatement': lambda: from_attrib('switchToken'),
        'ReturnStatement': lambda: from_attrib('returnToken'),
    }


    if node.nodeName in per_node_type:
        return per_node_type[node.nodeName]()

    return None

# For a given node, return a list of executable nodes that can be analyzed for coverage, if any.
def node_executable_subnodes(node):
    per_node_type = {
        'IfStatement': lambda: children_filter_nodes(node)[1:],
        'SwitchStatement': lambda: children_filter_nodes(node)[1:],
        'ForStatement': lambda: [ children_filter_nodes(node)[-1] ],
    }

    if node.nodeName in per_node_type:
        return per_node_type[node.nodeName]()

    return []

def is_single_statement(node):
    return node.nodeName in [
        'ExpressionStatement',
        'Statement',
    ]