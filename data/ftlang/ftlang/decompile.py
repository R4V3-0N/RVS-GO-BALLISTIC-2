#!/usr/bin/env python3

import sys
import re
import functools
from xml.etree.ElementTree import XMLParser, fromstring

from ftlang.prop_maps import simple_map, sound_map, stats_boost_map

def cmp(a, b):
    if a > b:
        return 1
    if a == b:
        return 0
    if a < b:
        return -1

# no sorting at all
# def weapons_cmp(w1, w2):
#     return 0

# type
# def weapons_cmp(w1, w2):
#     return cmp(w1.find('type').text, w2.find('type').text)

def weapons_cmp(w1, w2):
    n1 = w1.attrib['name']
    n2 = w2.attrib['name']
    r = cmp('ELITE' in n1, 'ELITE' in n2)
    if r != 0:
        return r
    return 0

sort_keys = {
    'weapons': functools.cmp_to_key(weapons_cmp),
}

def decompile(string):
    string = re.sub(re.compile('<!---+'), '<!--', string)
    string = re.sub(re.compile('---+>'), '-->', string)

    parser = XMLParser(encoding='utf-8')

    ftl_xml = fromstring(string, parser=parser)

    indent_level = 0

    def indent():
        nonlocal indent_level
        indent_level += 1

    def dedent():
        nonlocal indent_level
        indent_level -= 1

    output = []

    def add(*s):
        output.append('    ' * indent_level + ' '.join(s) + '\n')

    def pair(key, value):
        if str(value).isnumeric():
            add(key, '=', value)
        else:
            add(key + ':', str(value))

    for wb in sorted(ftl_xml.findall('weaponBlueprint'), key=sort_keys['weapons']):
        add('weapon {')
        indent()
        add(f'name: {wb.attrib["name"]}')
        for key in simple_map:
            value = simple_map[key]
            title_xml = wb.find(value['tag'])
            if title_xml is not None:
                pair(key, title_xml.text)
            elif 'opt' not in value['flags']:
                if 'default' in value:
                    pair(key, value["default"])
                else:
                    raise Exception(f'undefined {value["tag"]} on {wb.find("title").text}')
        
        stats_xml = wb.find('statBoosts')
        if stats_xml is not None:
            for stat_xml in sorted(stats_xml.findall('statBoost'), key=lambda x: x.attrib['name']):
                add('stats_boost {')
                indent()
                pair('name', stat_xml.attrib['name'])
                for key in stats_boost_map:
                    value = stats_boost_map[key]
                    found = stat_xml.find(value['tag'])
                    if found is not None:
                        if 'unless' not in value or found not in value['unless']:
                            pair(key, found.text)
                    elif 'flags' not in value or 'opt' not in value['flags']:
                        raise Exception(f'undefined stats boost {value["tag"]} on {wb.find("title").text}')
                dedent()
                add('}')
        projs_xml = wb.find('projectiles')
        if projs_xml is not None:
            for proj_xml in sorted(projs_xml.findall('projectile'), key=lambda x: x.text):
                add('projectile {')
                indent()
                if 'fake' in proj_xml.attrib and not proj_xml.attrib['fake']:
                    pair('fake', 'false')
                if 'blueprint' in proj_xml.attrib:
                    pair('blueprint', proj_xml.attrib['blueprint'])
                pair('texture', proj_xml.text)
                dedent()
                add('}')
        for sound_type in sound_map:
            sounds_xml = wb.find(sound_type)
            if sounds_xml is not None:
                add(sound_map[sound_type] + ': {')
                indent()
                for sound in sorted(sounds_xml.findall('sound'), key=lambda x: x.text):
                    add(sound.text)
                dedent()
                add('}')
        dedent()
        add('}')
        add()
    return output

def main():
    with open(sys.argv[1]) as file:
        string = file.read()
    lines = decompile(string)
    out = ''.join(lines)
    with open(sys.argv[2], 'w') as file:
        file.write(out)

if __name__ == '__main__':
    main()
