import re
from xml.etree.ElementTree import XMLParser, fromstring, parse

def run(src):

    src = re.sub(re.compile('<!---+'), '<!--', src)
    src = re.sub(re.compile('---+>'), '-->', src)

    parser = XMLParser(encoding='utf-8')

    ftl_xml = fromstring(src, parser=parser)

    elems = []

    for elem in ftl_xml.iter():
        elems.append(elem.tag)

    elems = list(set(elems))
    elems.sort()

    return elems

if __name__ == '__main__':
    with open('../blueprints.xml.append') as file:
        src = file.read()
    elems = run(src)
    for elem in elems:
        print(elem)
