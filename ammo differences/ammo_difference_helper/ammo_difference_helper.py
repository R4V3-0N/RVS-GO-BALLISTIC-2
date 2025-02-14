from codecs import BOM_UTF8
from enum import Enum
from io import TextIOWrapper
from multiprocessing import current_process
from typing import Any
from typing import Dict
import xml.parsers.expat as expat;

class ElementType:
    START = 1
    DATA = 2
    END = 3

BASE_WEAPONS = {"GB_AC_1", "GB_AC_2", "GB_AC_3", "GB_AC_1_ELITE", "GB_AC_2_ELITE", "GB_AC_3_ELITE"}
BLUEPRINTS_FILE = open("../../data/blueprints.xml.append", "rb")

in_weapon_node: bool = False
ammo_files: Dict[str, TextIOWrapper] = dict()
current_ammo_file: TextIOWrapper = None

def get_ammo_file(name: str):
    global ammo_files
    
    if name in ammo_files:
        return ammo_files[name]
    else:
        new_file = open(f"{name.lower()}.xml", "a", encoding="utf-8")
        ammo_files[name] = new_file
        return new_file

def start_handler(name: str, attributes: Dict[str, Any]):
    global in_weapon_node
    global current_ammo_file
    
    if name == "weaponBlueprint" and "name" in attributes:
        weapon_name: str = attributes["name"]
        split_name = weapon_name.split("_")
        base_name = "_".join(split_name[:-1])
        ammo_type = split_name[-1]

        if base_name in BASE_WEAPONS:
            in_weapon_node = True
            current_ammo_file = get_ammo_file(ammo_type)

    if in_weapon_node:
        current_ammo_file.write(f"<{name}")
        for attribute, value in attributes.items():
            current_ammo_file.write(f" {attribute}=\"{value}\"")
        current_ammo_file.write(">")

def data_handler(data: Any):
    global in_weapon_node
    global current_ammo_file

    if in_weapon_node:
        current_ammo_file.write(str(data).replace("\r\n", "\n"))

def end_handler(name: str):
    global in_weapon_node
    global current_ammo_file

    if in_weapon_node:
        current_ammo_file.write(f"</{name}>")
        if name == "weaponBlueprint":
            current_ammo_file.write("\n\n")
            in_weapon_node = False
            current_ammo_file = None

parser = expat.ParserCreate()
parser.StartElementHandler = start_handler
parser.CharacterDataHandler = data_handler
parser.EndElementHandler = end_handler
parser.ParseFile(BLUEPRINTS_FILE)

BLUEPRINTS_FILE.close()
for file in ammo_files.values():
    file.close()