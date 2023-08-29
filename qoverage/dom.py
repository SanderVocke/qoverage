import xml.dom
import xml.dom.minidom
import re

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

def token_offset(node, token_name, add_length=False):
    loc = token_loc(node, token_name)
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
    elif node_is(node, 'Node'):
        return parent_as(node, tag_name_or_names)
    return None

def parent_as(node, tag_name_or_names):
    return node_as(node.parentNode, tag_name_or_names)

def children_filter_nodes(node):
    def child(c):
        if node_is(c, 'Node'):
            return children_filter_nodes(c)[0]
        elif c.nodeType == xml.dom.Node.ELEMENT_NODE:
            return c
        return None
    
    return [child(c) for c in node.childNodes if child(c)]

def node_eval_start_offset(node):
    def from_attrib(attrib, add_length=False):
        return token_offset(node, attrib)
    
    per_node_type = {
        'BreakStatement': lambda: from_attrib('breakToken'),
        'ExpressionStatement': lambda: node_eval_start_offset(children_filter_nodes(node)[0]),
        'CallExpression': lambda: node_eval_start_offset(children_filter_nodes(node)[0]),
        'BinaryExpression': lambda: node_eval_start_offset(children_filter_nodes(node)[0]),
        'FieldMemberExpression':  lambda: node_eval_start_offset(children_filter_nodes(node)[0]),
        'IdentifierExpression': lambda: from_attrib('identifierToken'),
        'NumericLiteral': lambda: from_attrib('literalToken'),
        'ForStatement': lambda: from_attrib('forToken'),
        'IfStatement': lambda: from_attrib('ifToken'),
        'SwitchStatement': lambda: from_attrib('switchToken'),
        'ReturnStatement': lambda: from_attrib('returnToken'),
        # TODO Statement
        # TODO ThrowStatement
        # TODO TryStatement
        # TODO VariableStatement
        # TODO WhileStatement
    }

    if node.nodeName in per_node_type:
        return per_node_type[node.nodeName]()

    return None