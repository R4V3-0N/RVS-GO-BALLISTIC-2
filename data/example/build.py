#!/usr/bin/env python3

import sys
from copy import deepcopy
from fractions import Fraction
from xml.etree.ElementTree import Element, SubElement, indent, tostring

from lark import Lark, Token
from ftlang.maps import simple_map

parser = Lark.open("./ftlang/ftlang.lark")

def require_prop(obj, prop, default=None):
    assert len(prop) != 0
    if isinstance(prop, (list, tuple)):
        key = None
        for check in prop:
            if check in obj:
                if key is None:
                    key = check
                else:
                    raise Exception(f"you cannot set both {key} and {check}, as they do the same thing.")
        if key is None and default is None:
            if len(prop) == 1:
                raise Exception(f"you need to set {prop}.")
            elif len(prop) == 2:
                raise Exception(f"you need to set either {prop[0]} or {prop[1]}.")
            else:
                raise Exception(f"you need to set one of {', '.join(prop[:-1])}, or {prop[-1]}")
        prop = key
    if prop not in obj:
        if default is None:
            raise Exception(f"you need to set {prop}.")
        else:
            return default
    else:
        return obj[prop]

def require_props(obj, *props):
    ret = []
    for prop in props:
        if prop not in obj:
            raise Exception(f"you need to set {prop}.")
        else:
            ret.append(obj[prop])
    return ret

class Converter:
    def __init__(self):
        self.weapons = []
        self.scopes = []
        self.vars = {}

    def toxml(self):
        ftl = Element("FTL")
        for weapon in self.weapons:
            name = require_prop(weapon, 'name')
            
            wb = SubElement(ftl, "weaponBlueprint", {'name': name})

            print(weapon['name'])

            for key in simple_map:
                value = simple_map[key]
                result = weapon
                for path in key.split('.'):
                    if not isinstance(result, dict):
                        raise Exception(f"you need to set {key} differently.")
                    elif path in result:
                        result = result[path]
                    else:
                        if 'default' in value:
                            result = value['default']
                            break
                        elif 'opt' not in value['flags']:
                            raise Exception(f"you need to set {key}.")
                result = value['conv'](result)
                if 'unless' not in value or result not in value['unless']:
                    SubElement(wb, value['tag']).text = str(result)

            stats_boosts = require_prop(weapon, 'stats_boost', [])
            if len(stats_boosts) != 0:
                sboosts_xml = SubElement(wb, 'statBoosts')
            for stats_boost in stats_boosts:
                name = require_prop(stats_boost, 'name')
                single_xml = SubElement(sboosts_xml, 'statBoost', {'name': name})
                SubElement(single_xml, 'boostType').text = str(require_prop(stats_boost, 'type'))
                SubElement(single_xml, 'amount').text = str(require_prop(stats_boost, 'amount'))
                SubElement(single_xml, 'shipTarget').text = str(require_prop(stats_boost, 'ships', 'ALL'))
                SubElement(single_xml, 'crewTarget').text = str(require_prop(stats_boost, 'crew', 'ALL'))
                SubElement(single_xml, 'affectsSelf').text = str(require_prop(stats_boost, 'impacts_self'))
                SubElement(single_xml, 'duration').text = str(require_prop(stats_boost, 'duration'))
                SubElement(single_xml, 'animation').text = str(require_prop(stats_boost, 'animation'))
            projectiles = require_prop(weapon, 'projectile', [])
            if len(projectiles) != 0:
                projectiles_xml = SubElement(wb, 'projectiles')
            for projectile in projectiles:
                args = {}
                args['count'] = str(require_prop(projectile, 'count', 1))
                args['fake'] = str(require_prop(projectile, 'fake', 'false'))
                texture = str(require_prop(projectile, 'texture'))
                SubElement(projectiles_xml, 'projectile', args).text = texture
            sounds = require_prop(weapon, 'sounds', {})
            sounds_launch = require_prop(sounds, 'launch', [])
            sounds_miss = require_prop(sounds, 'miss', [])
            sounds_hit = require_prop(sounds, 'hit', {})
            sounds_hit_ship = require_prop(sounds_hit, 'ship', [])
            sounds_hit_shield = require_prop(sounds_hit, 'shield', [])
            map_sounds = {
                'launchSounds': sounds_launch,
                'hitShipSounds': sounds_hit_ship,
                'hitShieldsSounds': sounds_hit_shield,
                'missSoudns': sounds_miss
            }
            for key in map_sounds:
                value = map_sounds[key]
                sounds_xml = SubElement(wb, key)
                for sound in value:
                    SubElement(sounds_xml, 'sound').text = sound
                    
                
        return ftl
        
    def get(self, *args):
        vars = self.vars
        for i in args:
            vars = vars[i]
        return vars

    def set(self, *args):
        val = args[-1]
        op = args[-2]
        vars = self.vars
        for i in args[:-3]:
            if i not in vars:
                vars[i] = {}
            vars = vars[i]
        key = args[-3]
        match str(op):
            case "=":
                vars[key] = val
            case "+=":
                if isinstance(vars[key], list):
                    vars[key].append(val)
                else:
                    vars[key] += val
            case "-=":
                vars[key] -= val
            case "*=":
                vars[key] *= val
            case "/=":
                vars[key] /= val

    def stmts(self, ch):
        for c in ch:
            self.stmt(c)

    def expr(self, ast):
        if isinstance(ast, Token):
            match ast.type:
                case "NUMBER":
                    return Fraction(str(ast))
                case "NAME":
                    return self.get(str(ast))
                case "STRING":
                    return str(ast)
                case _:
                    raise Exception("bad type: " + ast.type)
        kind = ast.data
        ch = ast.children
        match kind:
            case "addexpr":
                if len(ch) == 1:
                    return self.expr(ch[0])
                elif str(ch[1]) == '+':
                    return self.expr(ch[0]) + self.expr(ch[2])
                elif str(ch[1]) == '-':
                    return self.expr(ch[0]) - self.expr(ch[2])
            case "mulexpr":
                if len(ch) == 1:
                    return self.expr(ch[0])
                elif str(ch[1]) == '*':
                    return self.expr(ch[0]) * self.expr(ch[2])
                elif str(ch[1]) == '/':
                    return self.expr(ch[0]) / self.expr(ch[2])
            case "dotexpr":
                obj = self.expr(ch[0])
                for i in ch[1:]:
                    obj = obj[i]
                return obj
            case "array" | "words_array":
                return [self.expr(i) for i in ch]
            case "single":
                return self.expr(ch[0])
            case _:
                raise Exception("bad type: " + kind)

    def stmt(self, ast):
        if isinstance(ast, Token):
            raise Exception(f"bad syntax: {str(ast)}")
        kind = ast.data
        ch = ast.children
        match kind:
            case "start":
                self.stmts(ch)
                return self
            case "block":
                try:
                    self.scopes.append(self.vars)
                    self.vars = deepcopy(self.vars)
                    block_name = str(ch[0])
                    match block_name:
                        case "weapon":
                            self.stmts(ch[1:])
                            self.weapons.append(self.vars)
                        case "with":
                            self.stmts(ch[1:])
                        case _:
                            last_vars = self.scopes[-1]
                            if block_name not in last_vars:
                                last_vars[block_name] = []
                            self.stmts(ch[1:])
                            last_vars[block_name].append(self.vars)
                finally:
                    self.vars = self.scopes.pop()
            case "stmt":
                self.stmts(ch)
            case "variant":
                raise Exception("bad variant")
            case "co_arr_assign":
                varname = [str(i) for i in ch[-2].children]
                value = [str(i) for i in ch[-1].children]
                self.set(*varname, '=', value)
            case "co_assign":
                varname = [str(i) for i in ch[-2].children]
                value = str(ch[-1]).strip()
                self.set(*varname, '=', value)
            case "eq_assign":
                varname = [str(i) for i in ch[-3].children]
                operator = ch[-2]
                value = self.expr(ch[-1])
                self.set(*varname, operator, value)
            case _:
                raise Exception("bad type: " + kind)

with open(sys.argv[1]) as file:
    ast = parser.parse(file.read())

convert = Converter()
convert.stmt(ast)
xml = convert.toxml()
indent(xml, space="\t", level=0)
result = tostring(xml).decode('utf-8')

with open(sys.argv[2], "w") as file:
    file.write(result)