from xml.etree.ElementTree import XMLParser, fromstring

from ftlang.maps import simple_map, sound_map

with open('input.xml') as file:
    string = file.read()

parser = XMLParser(encoding='utf-8')

ftl_xml = fromstring(string, parser=parser)

indent_level = 0

def indent():
    global indent_level
    indent_level += 1

def dedent():
    global indent_level
    indent_level -= 1

output = []

def add(*s):
    output.append('    ' * indent_level + ' '.join(s) + '\n')

for wb in ftl_xml.findall('weaponBlueprint'):
    add('weapon {')
    indent()
    add(f'name: {wb.attrib["name"]}')
    for key in simple_map:
        value = simple_map[key]
        title_xml = wb.find(value['tag'])
        if title_xml is not None:
            add(f'{key}: {title_xml.text}')
        elif 'opt' not in value['flags']:
            if 'default' in value:
                add(f'{key}: {value["default"]}')
            else:
                raise Exception(f'undefined {value["tag"]} on {wb.find("title").text}')
    for sound_type in sound_map:
        sounds_xml = wb.find(sound_type)
        if sound_type is not None:
            add(sound_map[sound_type], '{')
            indent()
            for sound in sorted(sounds_xml.findall('sound'), key=lambda x: x.text):
                add(sound.text)
            dedent()
            add('}')
    dedent()
    add('}')

with open('gen/output.ftlang', 'w') as file:
    file.write(''.join(output))
