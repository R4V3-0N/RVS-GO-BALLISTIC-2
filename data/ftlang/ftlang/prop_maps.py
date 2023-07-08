
from fractions import Fraction

simple_map = {
    'type': {
        'tag': 'type',
    },
    'title': {
        'tag': 'title',
        'flags': ['opt'],
    },
    'short': {
        'tag': 'short',
        'flags': ['opt'],
    },
    'description': {
        'tag': 'desc',
        'flags': ['opt'],
    },
    'tooltip': {
        'tag': 'tooltip',
        'flags': ['opt'],
    },
    'speed': {
        'tag': 'speed',
        'flags': ['opt'],
    },
    'shots': {
        'tag': 'shots',
        'default': 1,
    },
    'breach': {
        'tag': 'breachChance',
        'default': 0,
        'unless': [0],
    },
    'subtype': {
        'tag': 'flavor',
        'flags': ['opt'],
    },
    'damage.hull': {
        'tag': 'damage',
        'default': 0,
        'flags': ['opt'],
    },
    'damage.system': {
        'tag': 'sysDamage',
        'default': 0,
        'flags': ['opt'],
    },
    'damage.crew': {
        'tag': 'persDamage',
        'default': 0,
        'flags': ['opt'],
    },
    'pierce': {
        'tag': 'sp',
        'default': 0,
        'flags': ['opt'],
    },
    'breach': {
        'tag': 'breachChance',
        'default': 0,
        'unless': [0],
        'flags': ['opt'],
    },
    'rarity': {
        'tag': 'rarity',
        'default': 0,
    },
    'power': {
        'tag': 'power',
        'default': 1,
        'flags': ['opt'],
    },
    'cooldown': {
        'tag': 'cooldown',
        'flags': ['opt'],
    },
    'cost': {
        'tag': 'cost',
        'flags': ['opt'],
    },
    'art': {
        'tag': 'weaponArt',
    },
    'icon': {
        'tag': 'iconImage',
        'flags': ['opt'],
    }
}

sound_map = {
    'launchSounds': 'sounds.launch',
    'hitShipSounds': 'sounds.hit.ship',
    'hitShieldSounds': 'sounds.hit.shield',
    'missSounds': 'sounds.miss',
}

stats_boost_map = {
    'type': {
        'tag': 'boostType',
    },
    'amount': {
        'tag': 'amount',
        'flags': ['opt'],
    },
    'impacts_self': {
        'tag': 'affectsSelf',
    },
    'ships': {
        'tag': 'shipTarget',
        'unless': ['ALL'],
    },
    'crew': {
        'tag': 'crewTarget',
        'unless': ['ALL'],
    },
    'duration': {
        'tag': 'duration',
    },
    'animation': {
        'tag': 'boostAnim',
        'flags': ['opt'],
    },
}

def auto_str(s=''):
    if isinstance(s, Fraction):
        if s % 1 == 0:
            s = int(s)
        else:
            s = float(s)
    return str(s)

for v in simple_map.values():
    if 'conv' not in v:
        v['conv'] = auto_str
    if 'flags' not in v:
        v['flags'] = []
    if 'opt' in v['flags'] and 'default' not in v:
        v['default'] = v['conv']()
        v['unless'] = v['conv']()
