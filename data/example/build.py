#!/usr/bin/env python3

import sys
from copy import deepcopy
from fractions import Fraction
from xml.etree.ElementTree import Element, SubElement, indent, tostring

from lark import Lark, Token

parser = Lark.open("./build/ftlang.lark")

def require_prop(obj, prop):
    if prop not in obj:
        raise Exception("you need to set: " + prop)
    else:
        return obj[prop]

def require_props(obj, *props):
    ret = []
    for prop in props:
        if prop not in obj:
            raise Exception("you need to set: " + prop)
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
            print(weapon)
            wb = SubElement(ftl, "weaponBlueprint")
            SubElement(wb, "type").append(require_prop(weapon, 'type'))
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
            case "weapon":
                try:
                    self.scopes.append(self.vars)
                    self.vars = deepcopy(self.vars)
                    self.stmts(ch)
                    return self.weapons.append(self.vars)
                finally:
                    self.vars = self.scopes.pop()
            case "stmt":
                self.stmts(ch)
            case "variant":
                raise Exception("bad variant")
            case "co_assign":
                self.set(*[str(i) for i in ch[:-2]], '=', str(ch[-1]).strip())
            case "eq_assign":
                self.set(*[str(i) for i in ch[:-2]], ch[-2], self.expr(ch[-1]))
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
