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
        'WhileStatement': lambda: from_attrib('whileToken'),
        'PostIncrementExpression': lambda: node_eval_start_offset(children_filter_nodes(node)[0]),
        'DoWhileStatement': lambda: from_attrib('doToken'),
        'ArrayMemberExpression': lambda: node_eval_start_offset(children_filter_nodes(node)[0]),
        'ArrayPattern': lambda: from_attrib(['lbracketToken', 'lbraketToken']),
        'FunctionExpression': lambda: from_attrib('functionToken'),
        'TryStatement': lambda: from_attrib('tryToken'),
        'NullExpression': lambda: from_attrib('nullToken'),
        'ConditionalExpression': lambda: node_eval_start_offset(children_filter_nodes(node)[0]),
        'ThrowStatement': lambda: from_attrib('throwToken'),
        'NotExpression': lambda: from_attrib('notToken'),
        'NestedExpression': lambda: from_attrib('lparenToken'),
        'UnaryMinusExpression': lambda: from_attrib('minusToken'),
        #'Statement': TODO,
        #'TypeExpression': TODO,
        #'ThisExpression': TODO,
        #'SuperLiteral': TODO,
        #'TemplateLiteral': TODO,
        #'RegExpLiteral': TODO,
        #'Pattern': TODO,
        #'ObjectPattern': TODO,
        #'PatternElement': TODO,
        #'PatternElementList': TODO,
        #'PatternProperty': TODO,
        #'PatternPropertyList': TODO,
        #'Elision': TODO,
        #'PropertyName': TODO,
        #'IdentifierPropertyName': TODO,
        #'StringLiteralPropertyName': TODO,
        #'NumericLiteralPropertyName': TODO,
        #'ComputedPropertyName': TODO,
        #'TaggedTemplate': TODO,
        #'NewMemberExpression': TODO,
        #'NewExpression': TODO,
        #'ArgumentList': TODO,
        #'PostDecrementExpression': TODO,
        #'DeleteExpression': TODO,
        #'VoidExpression': TODO,
        #'TypeOfExpression': TODO,
        #'PreIncrementExpression': TODO,
        #'PreDecrementExpression': TODO,
        #'UnaryPlusExpression': TODO,
        #'TildeExpression': TODO,
        #'Expression': TODO,
        #'YieldExpression': TODO,
        #'Block': TODO,
        #'LeftHandSideExpression': TODO,
        #'StatementList': TODO,
        #'VariableDeclarationList': TODO,
        #'EmptyStatement': TODO,
        #'ForEachStatement': TODO,
        #'ContinueStatement': TODO,
        #'WithStatement': TODO,
        #'CaseBlock': TODO,
        #'CaseClauses': TODO,
        #'CaseClause': TODO,
        #'DefaultClause': TODO,
        #'LabelledStatement': TODO,
        #'Catch': TODO,
        #'Finally': TODO,
        #'FunctionDeclaration': TODO,
        #'FormalParameterList': TODO,
        #'ExportSpecifier': TODO,
        #'ExportsList': TODO,
        #'ExportClause': TODO,
        #'ExportDeclaration': TODO,
        #'Program': TODO,
        #'ImportSpecifier': TODO,
        #'ImportsList': TODO,
        #'NamedImports': TODO,
        #'NameSpaceImport': TODO,
        #'NamedImport': TODO,
        #'ImportClause': TODO,
        #'FromClause': TODO,
        #'ImportDeclaration': TODO,
        #'ESModule': TODO,
        #'DebuggerStatement': TODO,
        #'ClassExpression': TODO,
        #'ClassDeclaration': TODO,
        #'ClassElementList': TODO,
        #'Type': TODO,
        #'TypeAnnotation': TODO,
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
        'PostIncrementExpression': lambda: from_attrib('incrementToken', True),
        'ArrayMemberExpression': lambda: from_attrib(['rbracketToken', 'rbraketToken'], True),
        'ArrayPattern': lambda: from_attrib(['rbracketToken', 'rbraketToken'], True),
        'FunctionExpression': lambda: from_attrib('rbraceToken', True),
        'NullExpression': lambda: from_attrib('nullToken', True),
        'ConditionalExpression': lambda: node_eval_end_offset(children_filter_nodes(node)[-1]),
        'NotExpression': lambda: node_eval_end_offset(children_filter_nodes(node)[-1]),
        'NestedExpression': lambda: from_attrib('rparenToken', True),
        'UnaryMinusExpression': lambda: node_eval_end_offset(children_filter_nodes(node)[-1]),
        #'Statement': TODO,
        #'TypeExpression': TODO,
        #'ThisExpression': TODO,
        #'SuperLiteral': TODO,
        #'TemplateLiteral': TODO,
        #'RegExpLiteral': TODO,
        #'Pattern': TODO,
        #'ObjectPattern': TODO,
        #'PatternElementList': TODO,
        #'PatternProperty': TODO,
        #'PatternPropertyList': TODO,
        #'Elision': TODO,
        #'PropertyName': TODO,
        #'IdentifierPropertyName': TODO,
        #'StringLiteralPropertyName': TODO,
        #'NumericLiteralPropertyName': TODO,
        #'ComputedPropertyName': TODO,
        #'TaggedTemplate': TODO,
        #'NewMemberExpression': TODO,
        #'NewExpression': TODO,
        #'ArgumentList': TODO,
        #'PostDecrementExpression': TODO,
        #'DeleteExpression': TODO,
        #'VoidExpression': TODO,
        #'TypeOfExpression': TODO,
        #'PreIncrementExpression': TODO,
        #'PreDecrementExpression': TODO,
        #'UnaryPlusExpression': TODO,
        #'TildeExpression': TODO,
        #'Expression': TODO,
        #'YieldExpression': TODO,
        #'Block': TODO,
        #'LeftHandSideExpression': TODO,
        #'StatementList': TODO,
        #'EmptyStatement': TODO,
        #'IfStatement': TODO,
        #'DoWhileStatement': TODO,
        #'WhileStatement': TODO,
        #'ForStatement': TODO,
        #'ForEachStatement': TODO,
        #'ContinueStatement': TODO,
        #'WithStatement': TODO,
        #'SwitchStatement': TODO,
        #'CaseBlock': TODO,
        #'CaseClauses': TODO,
        #'CaseClause': TODO,
        #'DefaultClause': TODO,
        #'LabelledStatement': TODO,
        #'ThrowStatement': TODO,
        #'TryStatement': TODO,
        #'Catch': TODO,
        #'Finally': TODO,
        #'FunctionDeclaration': TODO,
        #'FormalParameterList': TODO,
        #'ExportSpecifier': TODO,
        #'ExportsList': TODO,
        #'ExportClause': TODO,
        #'ExportDeclaration': TODO,
        #'Program': TODO,
        #'ImportSpecifier': TODO,
        #'ImportsList': TODO,
        #'NamedImports': TODO,
        #'NameSpaceImport': TODO,
        #'NamedImport': TODO,
        #'ImportClause': TODO,
        #'FromClause': TODO,
        #'ImportDeclaration': TODO,
        #'ESModule': TODO,
        #'DebuggerStatement': TODO,
        #'ClassExpression': TODO,
        #'ClassDeclaration': TODO,
        #'ClassElementList': TODO,
        #'Type': TODO,
        #'TypeAnnotation': TODO,
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
        'WhileStatement': lambda: from_attrib('whileToken'),
        'DoWhileStatement': lambda: from_attrib('doToken'),
        'ThrowStatement': lambda: from_attrib('throwToken'),
        'ContinueStatement': lambda: from_attrib('continueToken'),
        'FunctionExpression': lambda: from_attrib('functionToken'),
        'TryStatement': lambda: from_attrib('tryToken'),
        #'Statement': TODO,
        #'TypeExpression': TODO,
        #'ThisExpression': TODO,
        #'IdentifierExpression': TODO,
        #'NullExpression': TODO,
        #'TrueLiteral': TODO,
        #'FalseLiteral': TODO,
        #'SuperLiteral': TODO,
        #'NumericLiteral': TODO,
        #'StringLiteral': TODO,
        #'TemplateLiteral': TODO,
        #'RegExpLiteral': TODO,
        #'Pattern': TODO,
        #'ArrayPattern': TODO,
        #'ObjectPattern': TODO,
        #'PatternElement': TODO,
        #'PatternElementList': TODO,
        #'PatternProperty': TODO,
        #'PatternPropertyList': TODO,
        #'Elision': TODO,
        #'PropertyName': TODO,
        #'IdentifierPropertyName': TODO,
        #'StringLiteralPropertyName': TODO,
        #'NumericLiteralPropertyName': TODO,
        #'ComputedPropertyName': TODO,
        #'ArrayMemberExpression': TODO,
        #'FieldMemberExpression': TODO,
        #'TaggedTemplate': TODO,
        #'NewMemberExpression': TODO,
        #'NewExpression': TODO,
        #'CallExpression': TODO,
        #'ArgumentList': TODO,
        #'PostIncrementExpression': TODO,
        #'PostDecrementExpression': TODO,
        #'DeleteExpression': TODO,
        #'VoidExpression': TODO,
        #'TypeOfExpression': TODO,
        #'PreIncrementExpression': TODO,
        #'PreDecrementExpression': TODO,
        #'UnaryPlusExpression': TODO,
        #'UnaryMinusExpression': TODO,
        #'TildeExpression': TODO,
        #'NotExpression': TODO,
        #'BinaryExpression': TODO,
        #'ConditionalExpression': TODO,
        #'Expression': TODO,
        #'YieldExpression': TODO,
        #'Block': TODO,
        #'LeftHandSideExpression': TODO,
        #'StatementList': TODO,
        #'VariableStatement': TODO,
        #'VariableDeclarationList': TODO,
        #'EmptyStatement': TODO,
        #'ExpressionStatement': TODO,
        #'ForEachStatement': TODO,
        #'WithStatement': TODO,
        #'CaseBlock': TODO,
        #'CaseClauses': TODO,
        #'CaseClause': TODO,
        #'DefaultClause': TODO,
        #'LabelledStatement': TODO,
        #'Catch': TODO,
        #'Finally': TODO,
        #'FunctionDeclaration': TODO,
        #'FormalParameterList': TODO,
        #'ExportSpecifier': TODO,
        #'ExportsList': TODO,
        #'ExportClause': TODO,
        #'ExportDeclaration': TODO,
        #'Program': TODO,
        #'ImportSpecifier': TODO,
        #'ImportsList': TODO,
        #'NamedImports': TODO,
        #'NameSpaceImport': TODO,
        #'NamedImport': TODO,
        #'ImportClause': TODO,
        #'FromClause': TODO,
        #'ImportDeclaration': TODO,
        #'ESModule': TODO,
        #'DebuggerStatement': TODO,
        #'NestedExpression': TODO,
        #'ClassExpression': TODO,
        #'ClassDeclaration': TODO,
        #'ClassElementList': TODO,
        #'Type': TODO,
        #'TypeAnnotation': TODO,
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
        'WhileStatement': lambda: [ children_filter_nodes(node)[1] ],
        'DoWhileStatement': lambda: [ children_filter_nodes(node)[0] ],
        'TryStatement': lambda: children_filter_nodes(node),
        'Catch': lambda: children_filter_nodes(node),
        #'Statement': TODO,
        #'TypeExpression': TODO,
        #'ThisExpression': TODO,
        #'IdentifierExpression': TODO,
        #'NullExpression': TODO,
        #'TrueLiteral': TODO,
        #'FalseLiteral': TODO,
        #'SuperLiteral': TODO,
        #'NumericLiteral': TODO,
        #'StringLiteral': TODO,
        #'TemplateLiteral': TODO,
        #'RegExpLiteral': TODO,
        #'Pattern': TODO,
        #'ArrayPattern': TODO,
        #'ObjectPattern': TODO,
        #'PatternElement': TODO,
        #'PatternElementList': TODO,
        #'PatternProperty': TODO,
        #'PatternPropertyList': TODO,
        #'Elision': TODO,
        #'PropertyName': TODO,
        #'IdentifierPropertyName': TODO,
        #'StringLiteralPropertyName': TODO,
        #'NumericLiteralPropertyName': TODO,
        #'ComputedPropertyName': TODO,
        #'ArrayMemberExpression': TODO,
        #'FieldMemberExpression': TODO,
        #'TaggedTemplate': TODO,
        #'NewMemberExpression': TODO,
        #'NewExpression': TODO,
        #'CallExpression': TODO,
        #'ArgumentList': TODO,
        #'PostIncrementExpression': TODO,
        #'PostDecrementExpression': TODO,
        #'DeleteExpression': TODO,
        #'VoidExpression': TODO,
        #'TypeOfExpression': TODO,
        #'PreIncrementExpression': TODO,
        #'PreDecrementExpression': TODO,
        #'UnaryPlusExpression': TODO,
        #'UnaryMinusExpression': TODO,
        #'TildeExpression': TODO,
        #'NotExpression': TODO,
        #'BinaryExpression': TODO,
        #'ConditionalExpression': TODO,
        #'Expression': TODO,
        #'YieldExpression': TODO,
        #'Block': TODO,
        #'LeftHandSideExpression': TODO,
        #'StatementList': TODO,
        #'VariableStatement': TODO,
        #'VariableDeclarationList': TODO,
        #'EmptyStatement': TODO,
        #'ExpressionStatement': TODO,
        #'ForEachStatement': TODO,
        #'ContinueStatement': TODO,
        #'BreakStatement': TODO,
        #'ReturnStatement': TODO,
        #'WithStatement': TODO,
        #'CaseBlock': TODO,
        #'CaseClauses': TODO,
        #'CaseClause': TODO,
        #'DefaultClause': TODO,
        #'LabelledStatement': TODO,
        #'ThrowStatement': TODO,
        #'Finally': TODO,
        #'FunctionDeclaration': TODO,
        #'FunctionExpression': TODO,
        #'FormalParameterList': TODO,
        #'ExportSpecifier': TODO,
        #'ExportsList': TODO,
        #'ExportClause': TODO,
        #'ExportDeclaration': TODO,
        #'Program': TODO,
        #'ImportSpecifier': TODO,
        #'ImportsList': TODO,
        #'NamedImports': TODO,
        #'NameSpaceImport': TODO,
        #'NamedImport': TODO,
        #'ImportClause': TODO,
        #'FromClause': TODO,
        #'ImportDeclaration': TODO,
        #'ESModule': TODO,
        #'DebuggerStatement': TODO,
        #'NestedExpression': TODO,
        #'ClassExpression': TODO,
        #'ClassDeclaration': TODO,
        #'ClassElementList': TODO,
        #'Type': TODO,
        #'TypeAnnotation': TODO,
    }

    if node.nodeName in per_node_type:
        return per_node_type[node.nodeName]()

    return []

def is_single_statement(node):
    return node.nodeName in [
        'ExpressionStatement',
        'Statement',
    ]