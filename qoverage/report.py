import logging
import xml.dom.minidom
import json
import os

logger = logging.getLogger('report')

def generate_report(coverages):

    imp = xml.dom.minidom.DOMImplementation()
    doctype = imp.createDocumentType(
        qualifiedName='coverage',
        publicId='', 
        systemId="http://cobertura.sourceforge.net/xml/coverage-04.dtd",
    )
    doc = imp.createDocument(None, 'coverage', doctype)

    root = doc.documentElement
    root.setAttribute('line-rate', '0.0')
    root.setAttribute('branch-rate', '0')
    root.setAttribute('lines-covered', '0')
    root.setAttribute('lines-valid', '0')
    root.setAttribute('branches-covered', '0')
    root.setAttribute('branches-valid', '0')
    root.setAttribute('complexity', '0')
    root.setAttribute('version', '6.5.0')
    root.setAttribute('timestamp', '0')

    sources = doc.createElement('sources')
    root.appendChild(sources)
    source = doc.createElement('source')
    sources.appendChild(source)
    source_text = doc.createTextNode('.')
    source.appendChild(source_text)

    packages = doc.createElement('packages')
    root.appendChild(packages)
    package = doc.createElement('package')
    packages.appendChild(package)
    package.setAttribute('name', '.')
    package.setAttribute('line-rate', '0.0')
    package.setAttribute('branch-rate', '0')
    package.setAttribute('complexity', '0')

    classes = doc.createElement('classes')
    package.appendChild(classes)

    for file,coverage in coverages.items():
        _class = doc.createElement('class')
        classes.appendChild(_class)
        _class.setAttribute('name', os.path.basename(file))
        _class.setAttribute('filename', file)
        _class.setAttribute('line-rate', '0.0')
        _class.setAttribute('branch-rate', '0')
        _class.setAttribute('complexity', '0')

        methods = doc.createElement('methods')
        _class.appendChild(methods)

        lines = doc.createElement('lines')
        _class.appendChild(lines)

        coverage_data = json.loads(coverage)
        for l in range(len(coverage_data)):
            result = coverage_data[l]
            if result != None:
                line = doc.createElement('line')
                line.setAttribute('number', str(l + 1))
                line.setAttribute('hits', str(result))
                lines.appendChild(line)

    xml_str = doc.toprettyxml(indent='  ')
    return xml_str