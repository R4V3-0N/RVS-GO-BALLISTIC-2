import re
from xml.etree.ElementTree import XMLParser, fromstring, parse
# load and parse the file

with open('../blueprints.xml.append') as file:
    string = file.read()

string = re.sub(re.compile('<!---+'), '<!--', string)
string = re.sub(re.compile('---+>'), '-->', string)

parser = XMLParser(encoding='utf-8')

ftl_xml = fromstring(string, parser=parser)

elemList = []

for elem in ftl_xml.iter():
    elemList.append(elem.tag)

# now I remove duplicities - by convertion to set and back to list
elemList = list(set(elemList))

# Just printing out the result
for elem in sorted(elemList):
    print(elem)
    