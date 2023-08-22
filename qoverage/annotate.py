import logging
import copy
import os

from string import Template
from .qmldom import QMLDom
from .dom import *
import json

logger = logging.getLogger('pre_annotate')

script_dir = os.path.dirname(os.path.abspath(__file__))

block_start_tag='START_EXEC_BLOCK'
block_end_tag='END_EXEC_BLOCK'
obj_start_tag='START_OBJ'
obj_end_tag='END_OBJ'

def format_annotation(tag, id):
    return ' /*@QOVERAGE:{}:{}*/ '.format(tag, id)

def annotation_finder(tag, id=None):
    if id != None:
        return r'/\*@QOVERAGE:' + tag + r':' + str(id) + '\*/'
    return r'/\*@QOVERAGE:' + tag + r':(\d+)\*/'

# An exec block is a range of statements that are executed together.
# A prerequisite for this is that executing the first statement guarantees
# executing the rest of them, including any sub-statements, the only exception
# being if a statement implicitly throws an exception.
# That means we need special handling of things like branches, throws, returns, loops etc.
def start_exec_block_annotation(id):
    return format_annotation(block_start_tag, id)
def end_exec_block_annotation(id):
    return format_annotation(block_end_tag, id)

# An object annotation marks a QML UI object. Only the opening and closing braces
# of the object are marked. The rest of the contents will not be getting coverage information
# unless it falls in another detection (e.g. another object, function, ...)
def start_obj_annotation(id):
    return format_annotation(obj_start_tag, id)
def end_obj_annotation(id):
    return format_annotation(obj_end_tag, id)

def pre_annotate(contents, qmldom : QMLDom = None, debug=False) -> str:
    if not qmldom:
        qmldom = QMLDom()
    dom = qmldom.ast_dom(contents)
    if not dom:
        raise Exception('Failed to parse QML file')
    
    annotations = []
    annotation_id = 0

    def add_annotation(offset, annotation):
        annotations.append({
            'offset': offset,
            'annotation': annotation
        })
    
    def next_annotation():
        nonlocal annotation_id
        annotation_id += 1
    
    def apply_annotations():
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

    def handle_stmts(stmts, start_offset):
        # We always know the start. The end we have to find.
        # The trigger is where we can inject an instrumentation to activate
        # the coverage.
        end_offset = None

        # The end depends on what we encounter on the way.
        for idx,stmt in enumerate(stmts):
            if node_is(stmt, 'ReturnStatement'):
                end_offset = token_offset(stmt, 'returnToken')
                # this is where our block ends. However, also make a new
                # block for anything that comes after this. It will never
                # be executed, but should be tracked as coverage-eligible.
                rest = stmts[idx+1:]
                if len(rest) > 0:
                    handle_stmts(stmts[idx+1:])
                break
            elif node_is(stmt, 'IfStatement'):
                end_offset = token_offset(stmt, 'ifToken')
                # this is where our block ends. However, also make a new
                # block for anything that comes after the if statement. It will never
                # be executed, but should be tracked as coverage-eligible.
                maybe_else = token_offset(stmt, 'elseToken')
                blk = node_as(children_filter_nodes(stmt)[1], 'Block') if not maybe_else else node_as(children_filter_nodes(stmt)[2], 'Block')
                if blk:
                    # TODO support block-less expressions
                    rest = stmts[idx+1:]
                    if len(rest) > 0:
                        handle_stmts(stmts[idx+1:], token_offset(blk, 'rbraceToken') + 1)
                break
        
        if end_offset is None:
            end_offset = token_offset(as_block, 'rbraceToken')

        add_annotation(start_offset, start_exec_block_annotation(annotation_id))
        add_annotation(end_offset, end_exec_block_annotation(annotation_id))
        next_annotation()

    def handle_obj(obj):
        parent_definition = parent_as(obj, 'UiObjectDefinition')
        if parent_definition:
            id = node_as(children_filter_nodes(parent_definition)[0], 'UiQualifiedId')
            if id:
                name = id.getAttribute('name')
                if name not in [ 'anchors', 'Timer', 'Repeater', 'Connections', 'Component' ]:
                    add_annotation(token_offset(obj, 'lbraceToken') + 1, start_obj_annotation(annotation_id))
                    add_annotation(token_offset(obj, 'rbraceToken'), end_obj_annotation(annotation_id))
                    next_annotation()

    for stmts in dom.getElementsByTagName('StatementList'):
        as_block = parent_as(stmts, ['Block', 'FunctionDeclaration'])
        if as_block:
            handle_stmts(children_filter_nodes(stmts), token_offset(as_block, 'lbraceToken') + 1)
    
    for obj in dom.getElementsByTagName('UiObjectInitializer'):
        handle_obj(obj)
    
    result = apply_annotations()
    logger.debug('Pre-annotated:\n{}'.format(result))
    return result

def generate_db_js(db, n_lines):
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
        'include_lines': json.dumps(list(include_lines))
    }

    with open(script_dir + '/templates/file_tracker.template.js', 'r') as f:
        src = Template(f.read())
        return src.substitute(template_subs)


def final_annotate(pre_annotated: str, db_lib_name: str, debug=False) -> str:
    result = copy.deepcopy(pre_annotated)

    # Scan markers and create the coverage database
    db = {}
    def db_add_exec_block(id, start, end):
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
    for match in re.finditer(annotation_finder(block_start_tag), result):
        id = int(match.group(1))
        start_line = result.count('\n', 0, match.start())
        end_match = re.search(annotation_finder(block_end_tag, id), result)
        if not end_match:
            logger.error('Annotation error: could not find end of exec block with id {}'.format(id))
            exit(1)
        end_line = result.count('\n', 0, end_match.start())
        db_add_exec_block(id, start_line, end_line)
    for match in re.finditer(annotation_finder(obj_start_tag), result):
        id = int(match.group(1))
        start_line = result.count('\n', 0, match.start())
        end_match = re.search(annotation_finder(obj_end_tag, id), result)
        if not end_match:
            logger.error('Annotation error: could not find end of object with id {}'.format(id))
            exit(1)
        end_line = result.count('\n', 0, end_match.start())
        db_add_obj(id, start_line, end_line)
    db_js = generate_db_js(db, pre_annotated.count('\n') + 1)

    def object_creation_marker():
        if debug:
            return r'\nproperty QtObject __qoverage_creation_tracker: QtObject {  Component.onCompleted: { console.log("[qoverage] create obj \1"); QoverageTracker.trace_obj_create(\1) } }\n'
        else:
            return r'\nproperty QtObject __qoverage_creation_tracker: QtObject {  Component.onCompleted: QoverageTracker.trace_obj_create(\1) }\n'
    
    def exec_marker():
        if debug:
            return r'; console.log("[qoverage] exec block \1"); QoverageTracker.trace_exec_block(\1); '
        else:
            return r'; QoverageTracker.trace_exec_block(\1); '

    # Do the actual code injection
    result = "{}\n\n{}".format(
        'import "./{}" as QoverageTracker'.format(db_lib_name),
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
        annotation_finder(block_start_tag),
        r'',
        result
    )
    result = re.sub(
        annotation_finder(block_end_tag),
        exec_marker(),
        result
    )

    logger.debug('Fully annotated:\n{}'.format(result))
    return result, db_js