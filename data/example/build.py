#!/usr/bin/env python3

import sys
from copy import deepcopy
from fractions import Fraction
from xml.etree.ElementTree import Element, SubElement, indent, tostring

from lark import Lark, Token

parser = Lark.open("./build/ftlang.lark")

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

            _type = require_prop(weapon, 'type')
            SubElement(wb, "type").text = _type

            title = require_prop(weapon, 'title')
            title_full = require_prop(title, 'full') if isinstance(title, dict) else title
            SubElement(wb, "title").text = title_full
            title_short = require_prop(title, 'short', title_full)
            SubElement(wb, "short").text = title_short

            description = require_prop(weapon, ('description', 'desc'))
            SubElement(wb, "desc").text = description

            tooltip = require_prop(weapon, 'tooltip', '')
            if len(tooltip) != 0:
                SubElement(wb, 'tooltip').text = tooltip
            
            flavor = require_prop(weapon, ('flavor', 'flavour'), '')
            if len(flavor) != 0:
                SubElement(wb, 'flavorType').text = flavor

            ammo = require_prop(weapon, ('missiles', 'ammo'), {})
            if isinstance(ammo, str):
                free_chance = (1 - float(ammo)) * 100
                SubElement(wb, 'missiles').text = '1'
                SubElement(wb, 'freeMissileChance').text = str(int(free_chance))
            else:
                missiles = require_prop(ammo, 'base', 0)
                free_chance = require_prop(ammo, 'free', 0)
                if missiles < 0:
                    raise Exception("weapon missile base usage souldn't be negative (i don't think)")
                elif missiles == 0:
                    pass
                elif missiles % 1 == 0:
                    SubElement(wb, 'missiles').text = str(int(missiles))
                    if free_chance != 0:
                        SubElement(wb, 'freeMissileChance').text = str(int(free_chance))
                else:
                    raise Exception("the developer of this program math'd wrong")
            
            damage = require_prop(weapon, 'damage', {})
            damage_hull = require_prop(damage, 'hull', 0)
            damage_system = require_prop(damage, ('system', 'room'), 0)
            damage_crew = require_prop(damage, ('crew', 'pers', 'personnel'), 0)
            if damage_hull != 0:
                SubElement(wb, 'damage').text = str(int(damage_hull))
            if damage_system != 0:
                SubElement(wb, 'sysDamage').text = str(int(damage_system))
            if damage_crew != 0:
                SubElement(wb, 'persDamage').text = str(int(damage_system))


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
            case "single":
                return self.expr(ch[0])
            case _:
                raise Exception("bad type: " + kind)

    def stmt(self, ast):
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
                    match str(ch[0]):
                        case "weapon":
                            self.stmts(ch)
                            self.weapons.append(self.vars)
                        case "stats_boost":
                            last_vars = self.scopes[-1]
                            if 'stats_boosts' not in last_vars:
                                last_vars['stats_boosts'] = []
                            self.scopes[-1]['stats_boosts'].append(self.vars)
                finally:
                    self.vars = self.scopes.pop()
            case "stmt":
                self.stmts(ch)
            case "variant":
                raise Exception("bad variant")
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
print(result)

with open(sys.argv[2], "w") as file:
    file.write(result)
