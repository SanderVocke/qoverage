import logging
import copy
import os

from string import Template
from .qmldom import QMLDom
from .dom import *
import json

logger = logging.getLogger('pre_annotate')

script_dir = os.path.dirname(os.path.abspath(__file__))

exec_block_start_tag='START_EXEC_BLOCK'
exec_block_end_tag='END_EXEC_BLOCK'
obj_start_tag='START_OBJ'
obj_end_tag='END_OBJ'
block_with_return_start_tag='OPEN_RETURN_BLOCK'
block_start_tag='OPEN_BLOCK'
block_end_tag='CLOSE_BLOCK'

# Don't annotate these objects (usually they are attached properties, qmldom doesn't know the difference)
objects_blacklist = [
    'anchors',
    'drag',
    'Timer',
    'Repeater',
    'Connections',
    'Component'
]

# Don't annotate these properties. They are represented as
# regexes, to be compared with found properties which are formatted as ObjectName::propertyName.
properties_blacklist = [
    'TestCase::name', # Must be a literal string for qmltestrunner
    '.*::id',         # id's should always be literals
]

def format_annotation(tag, id):
    """Formats an annotation with a tag and ID.
    
    Args:
        tag (str): The tag for the annotation.
        id (str): The ID for the annotation.
    
    Returns:
        str: A formatted annotation string.
    """
    
    return ' /*@QOVERAGE:{}:{}*/ '.format(tag, id)

def annotation_finder(tag, id=None):
    ```
    """Generates a regular expression pattern for finding QOVERAGE annotations in code.
    
    Args:
        tag (str): The tag to search for in the annotation.
        id (int, optional): The specific ID to match. If None, matches any numeric ID.
    
    Returns:
        str: A regular expression pattern for matching QOVERAGE annotations.
    """
    
    ```    if id != None:
        return r'/\*@QOVERAGE:' + tag + r':' + str(id) + '\*/'
    return r'/\*@QOVERAGE:' + tag + r':(\d+)\*/'

# An exec block is a range of statements that are executed together.
# A prerequisite for this is that executing the first statement guarantees
# executing the rest of them, including any sub-statements, the only exception
# being if a statement implicitly throws an exception.
# That means we need special handling of things like branches, throws, returns, loops etc.
def start_exec_block_annotation(id):
    ```
    """Formats and returns an execution block start annotation.
    
    Args:
        id (str): The identifier for the execution block.
    
    Returns:
        str: The formatted execution block start annotation.
    """
    ```
    return format_annotation(exec_block_start_tag, id)
def end_exec_block_annotation(id):
    ```
    """
    Formats and returns the end annotation for an execution block.
    
    Args:
        id (str): The unique identifier for the execution block.
    
    Returns:
        str: The formatted end annotation for the execution block.
    """
    ```
    return format_annotation(exec_block_end_tag, id)

# An object annotation marks a QML UI object. Only the opening and closing braces
# of the object are marked. The rest of the contents will not be getting coverage information
# unless it falls in another detection (e.g. another object, function, ...)
def start_obj_annotation(id):
    ```
    """Generates the start annotation for an object.
    
    Args:
        id (str): The unique identifier for the object.
    
    Returns:
        str: The formatted start annotation tag for the object.
    """
    ```
    return format_annotation(obj_start_tag, id)
def end_obj_annotation(id):
    return format_annotation(obj_end_tag, id)

# An expression to return block annotation marks an expression which is used as a
# script binding. We want to turn it into a block which returns the expression.
def block_open_with_return_annotation(id):
    ```
    """
    Formats a block opening tag with a return annotation.
    
    Args:
        id (str): The identifier for the block.
    
    Returns:
        str: The formatted block opening tag with return annotation.
    """
    ```
    return format_annotation(block_with_return_start_tag, id)
def block_close_annotation(id):
    return format_annotation(block_end_tag, id)
def block_open_annotation(id):
    return format_annotation(block_start_tag, id)

def is_block_open(annotation_text):
    ```
    """Check if a block is open in the annotation text.
    
    Args:
        annotation_text (str): The text to search for block start tags.
    
    Returns:
        bool: True if a block start tag is found, False otherwise.
    """
    ```
    return annotation_text.find(block_start_tag) != -1 or \
           annotation_text.find(block_with_return_start_tag) != -1

def is_block_close(annotation_text):
    return annotation_text.find(block_end_tag) != -1

# Add marker tags in QML files which can later be used to inject code.
# returns a tuple of (annotated code, QMLDom output)
def pre_annotate(contents, qmldom : QMLDom = None, filename='(unknown file)', debug=False) -> str:
    if not qmldom:
        qmldom = QMLDom()
    dom, ast_str = qmldom.ast_dom(contents)
    if not dom:
        raise Exception('Failed to parse QML file')
    
    annotations = []
    annotation_id = 0

    def add_annotation(offset, annotation):
        ```
        """
        Adds an annotation to the list of annotations.
        
        Args:
            offset (int): The offset position of the annotation.
            annotation (str): The content of the annotation.
        
        Returns:
            None
        """
        ```
        annotations.append({
            'offset': offset,
            'annotation': annotation
        })
    
    def next_annotation():
        nonlocal annotation_id
        annotation_id += 1
    
    def apply_annotations():
        """Apply annotations to the contents.
        
        Args:
            None
        
        Returns:
            str: A new string with annotations applied to the original contents.
        """
        
        def annot_sorter(a):
            return a['offset']
        
        new_contents = copy.deepcopy(contents)
        _annots = sorted(annotations,  key=annot_sorter)
        additional_offset = 0

        for annot in _annots:
            offset = annot['offset'] + additional_offset
            new_contents = new_contents[:offset] + annot['annotation'] + new_contents[offset:]
            additional_offset += len(annot['annotation'])
        
        return new_contents

    def visit_node(node, object_stack=[]):
        # By default, visit all children. Special cases may override below
        children_to_visit = children_filter_nodes(node)
        entered_object = None

        # Special cases
        if node.nodeName == 'StatementList':
            stmts = children_filter_nodes(node)
            rest_stmts = []

            # For statement lists, we try to insert an execution block marker at the start and
            # end, for any statements which are "guaranteed" to be executed together (the only
            # exception being a throw along the way, but we accept that inaccuracy).
            # Look for the first N statements that satisfy this requirement.
            start_offset = node_eval_start_offset(stmts[0])
            end_offset = None

            # Also, we don't want to visit all the children, only the ones not part of normal
            # linear execution.
            children_to_visit = []
            for idx,stmt in enumerate(stmts):
                end_offset = maybe_node_linear_execution_end_offset(stmt)
                children_to_visit = children_to_visit + node_executable_subnodes(stmt)
                if end_offset != None:
                    rest_stmts = stmts[idx+1:]
                    break
            
            if end_offset == None:
                # There were no nodes which explicitly end execution. In that case,
                # just insert the marker after the last statement.
                end_offset = node_eval_end_offset(stmts[-1])
            
            if end_offset == None:
                logger.warning(f"{filename}: No execution analysis for statement list because no execution endpoint found")
                logger.debug("Node XML:\n{}".format(
                    node.toxml()
                ))
            if start_offset == None:
                logger.warning(f"{filename}: No execution analysis for statement list because no execution start point found")
                logger.debug("Node XML:\n{}".format(
                    node.toxml()
                ))
            
            if start_offset != None and end_offset != None:
                add_annotation(start_offset, start_exec_block_annotation(annotation_id))
                add_annotation(end_offset, end_exec_block_annotation(annotation_id))
                next_annotation()
            
            if len(rest_stmts) > 0 and rest_stmts[0].nodeName == 'Catch':
                # Special handling of a catch (usually after a try just before):
                # skip the catch for exec block analysis, just make sure to visit
                # its child block.
                children_to_visit.append(node_executable_subnodes(rest_stmts[0]))
                rest_stmts = rest_stmts[1:]
            if len(rest_stmts) > 0:
                # There are "left-over" statements after the point where our linear execution ended.
                # Construct a statement list for the rest of the statements.
                rest_doc = xml.dom.minidom.Document()
                rest_list = rest_doc.createElement('StatementList')
                for rest_stmt in rest_stmts:
                    rest_list.appendChild(rest_stmt.cloneNode(deep=True))
                children_to_visit.append(rest_list)

        elif node.nodeName == 'UiObjectInitializer':
            # For object initializers, we want to mark the opening and closing braces
            # of the object. We still visit all its children too.
            # in addition, also keep a stack of objects so we always know what our current
            # object is.
            parent_definition = parent_as(node, 'UiObjectDefinition')
            if parent_definition:
                id = node_as(children_filter_nodes(parent_definition)[0], 'UiQualifiedId')
                if id:
                    name = id.getAttribute('name')
                    entered_object = name
                    global objects_blacklist
                    if name not in objects_blacklist:
                        add_annotation(token_offset(node, 'lbraceToken') + 1, start_obj_annotation(annotation_id))
                        add_annotation(token_offset(node, 'rbraceToken'), end_obj_annotation(annotation_id))
                        next_annotation()
        
        elif is_single_statement(node):
            # This should only happen as a result of visiting a UI script binding or e.g. if/else branch without block.
            # The expression should be wrapped in a block which returns the expression.
            children_to_visit = [] # this is a dead-end.
            start_offset = node_eval_start_offset(node)
            end_offset = node_eval_end_offset(node)
            if start_offset == None:
                logger.warning(f"{filename}: No execution analysis for {node.nodeName} because no execution start point found")
                logger.debug("Node XML:\n{}".format(
                    node.toxml()
                ))
            if end_offset == None:
                logger.warning(f"{filename}: No execution analysis for {node.nodeName} because no execution end point found")
                logger.debug("Node XML:\n{}".format(
                    node.toxml()
                ))
            if start_offset != None and end_offset != None:
                if parent_as(node, 'UiScriptBinding'):
                    # Script bindings need the result value to be returned.
                    # Exception is the id: binding, which is special and may not have any function block.
                    field = children_filter_nodes(parent_as(node, 'UiScriptBinding'))[0].getAttribute('name')
                    object_name = object_stack[-1] if len(object_stack) > 0 else None
                    formatted_field = object_name + '::' + field if object_name else field
                    # If the property matches any in our blacklist, don't annotate it.
                    if len(list(filter(lambda x: re.match(x, formatted_field), properties_blacklist))) == 0:
                        add_annotation(start_offset, block_open_with_return_annotation(annotation_id))
                        add_annotation(end_offset, block_close_annotation(annotation_id))
                        next_annotation()
                elif parent_as(node, 'UiPublicMember'):
                    # These (e.g. property definitions) need the result value to be returned.
                    # Exception is if the property is an alias, then it needs to directly reference
                    # another property without instrumentation in-between.
                    property_kind_node = children_filter_nodes(parent_as(node, 'UiPublicMember'))[0]
                    is_alias = property_kind_node.nodeName == 'UiQualifiedId' and property_kind_node.getAttribute('name') == 'alias'
                    if not is_alias:
                        add_annotation(start_offset, block_open_with_return_annotation(annotation_id))
                        add_annotation(end_offset, block_close_annotation(annotation_id))
                        next_annotation()
                else:
                    add_annotation(start_offset, block_open_annotation(annotation_id))
                    add_annotation(end_offset, block_close_annotation(annotation_id))
                    next_annotation()
        
        new_object_stack = copy.copy(object_stack)
        if entered_object:
            new_object_stack.append(entered_object)
        for child in children_to_visit:
            visit_node(child, new_object_stack)

    visit_node(dom)
    
    result = apply_annotations()
    return (result, ast_str)

def generate_db_js(db, n_lines, debug=False):
    ```
    """Generate JavaScript code for database tracking based on input parameters.
    
    Args:
        db (dict): A dictionary containing database information with keys as IDs and values as property dictionaries.
        n_lines (int): The total number of lines in the file being processed.
        debug (bool, optional): Flag to enable debug mode. Defaults to False.
    
    Returns:
        str: Generated JavaScript code for database tracking.
    """
    ```
    n_annotations = max(db.keys()) + 1
    ids_to_lines = {}
    include_lines = set()
    for (id, props) in db.items():
        if props['type'] == 'exec_block':
            # Mark whole block
            lines = list(range(props['start'], props['end'] + 1))
            logger.debug('gen DB for {}: lines {}'.format(id, lines))
            include_lines.update(lines)
            ids_to_lines[id] = lines
        elif props['type'] == 'object':
            # Mark opening of object
            lines = [props['start']]
            logger.debug('gen DB for {}: lines {}'.format(id, lines))
            include_lines.update(lines)
            ids_to_lines[id] = lines
    template_subs = {
        'n_annotations': n_annotations,
        'n_lines': n_lines,
        'ids_to_lines': json.dumps(ids_to_lines),
        'include_lines': json.dumps(list(include_lines)),
        'debug': ('true' if debug else 'false')
    }

    with open(script_dir + '/templates/file_tracker.template.js', 'r') as f:
        src = Template(f.read())
        return src.substitute(template_subs)


def final_annotate(pre_annotated: str, db_lib_name: str, debug=False) -> str:
    ```
    """Performs final annotation on pre-annotated code and generates coverage database.
    
    Args:
        pre_annotated (str): The pre-annotated code string.
        db_lib_name (str): The name of the database library.
        debug (bool, optional): Flag to enable debug mode. Defaults to False.
    
    Returns:
        tuple: A tuple containing:
            - str: The fully annotated code string.
            - str: The generated JavaScript code for the coverage database.
    """
    ```
    
    result = copy.deepcopy(pre_annotated)

    # Scan markers and create the coverage database
    db = {}
    def db_add_exec_block(id, start, end):
        """Add an execution block to the database.
        
        Args:
            id (str): The unique identifier for the execution block.
            start (int or float): The start time of the execution block.
            end (int or float): The end time of the execution block.
        
        Returns:
            None: This function doesn't return anything.
        """
        
        logger.debug("Add exec_block {}: {}-{}".format(id, start, end))
        db[id] = {
            'type': 'exec_block',
            'start': start,
            'end': end
        }
    def db_add_obj(id, start, end):
        logger.debug("Add obj {}: {}-{}".format(id, start, end))
        db[id] = {
            'type': 'object',
            'start': start,
            'end': start
        }
    for match in re.finditer(annotation_finder(exec_block_start_tag), result):
        id = int(match.group(1))
        start_line = result.count('\n', 0, match.start())
        end_match = re.search(annotation_finder(exec_block_end_tag, id), result)
        if not end_match:
            logger.error('Annotation error: could not find end of exec block with id {}'.format(id))
            exit(1)
        end_line = result.count('\n', 0, end_match.start())
        db_add_exec_block(id, start_line, end_line)
    for match in re.finditer(annotation_finder(block_with_return_start_tag), result):
        id = int(match.group(1))
        start_line = result.count('\n', 0, match.start())
        db_add_exec_block(id, start_line, start_line)
    for match in re.finditer(annotation_finder(block_start_tag), result):
        id = int(match.group(1))
        start_line = result.count('\n', 0, match.start())
        db_add_exec_block(id, start_line, start_line)
    for match in re.finditer(annotation_finder(obj_start_tag), result):
        id = int(match.group(1))
        start_line = result.count('\n', 0, match.start())
        end_match = re.search(annotation_finder(obj_end_tag, id), result)
        if not end_match:
            logger.error('Annotation error: could not find end of object with id {}'.format(id))
            exit(1)
        end_line = result.count('\n', 0, end_match.start())
        db_add_obj(id, start_line, end_line)
    db_js = generate_db_js(db, pre_annotated.count('\n') + 1, debug=debug)

    def object_creation_marker():
        if debug:
            return r'\nproperty QtObject __qoverage_creation_tracker: QtObject {  Component.onCompleted: { console.log("[qoverage] create obj \1"); QoverageCollector.trace_obj_create(\1) } }\n'
        else:
            return r'\nproperty QtObject __qoverage_creation_tracker: QtObject {  Component.onCompleted: QoverageCollector.trace_obj_create(\1) }\n'
    
    def exec_marker():
        if debug:
            return r'; console.log("[qoverage] exec block \1"); QoverageCollector.trace_exec_block(\1); '
        else:
            return r'; QoverageCollector.trace_exec_block(\1); '

    # Do the actual code injection
    result = "{}\n{}\n\n{}".format(
        'import QoverageSingleton 1.0 as QoverageSingleton',
        'import "./{}" as QoverageCollector'.format(db_lib_name),
        result
    )
    # object initialization
    result = re.sub(
        annotation_finder(obj_start_tag),
        object_creation_marker(),
        result
    )
    result = re.sub(
        annotation_finder(obj_end_tag),
        r'',
        result
    )
    result = re.sub(
        annotation_finder(exec_block_start_tag),
        r'',
        result
    )
    result = re.sub(
        annotation_finder(exec_block_end_tag),
        exec_marker(),
        result
    )
    result = re.sub(
        annotation_finder(block_with_return_start_tag),
        r'{ ' + exec_marker() + r'; return ',
        result
    )
    result = re.sub(
        annotation_finder(block_start_tag),
        r'{ ' + exec_marker() + r'; ',
        result
    )
    result = re.sub(
        annotation_finder(block_end_tag),
        r' }',
        result
    )

    #logger.debug('Fully annotated:\n{}'.format(result))
    return result, db_js