larkfile = """
start: stmt+

stmt: eq_assign | co_assign | co_arr_assign | block

block: target "{" (stmt | ":" WORDS)* "}"

eq_assign: target EQOP addexpr
co_assign: target ":" WORDS
co_arr_assign: target ":" words_array

addexpr: (mulexpr ADDOP)* mulexpr

mulexpr: (single MULOP)* single

dotexpr: single ("." NAME)*

single: NAME | NUMBER | STRING | array

array: "{" addexpr "}"
words_array: "{" WORDS* "}"

target: NAME ("." NAME)*

EQOP: "+=" | "*=" | "-=" | "/=" | "="
ADDOP: "+" | "-"
MULOP: "*" | "/"

WORDS: /[^\\n{}]+/

%ignore SPACE

%ignore /\s*(\/\/|--|#)[^\\n]*/

NUMBER: SIGNED_NUMBER | UNSIGNED_NUMBER

%import common.CNAME -> NAME
%import common.NUMBER -> UNSIGNED_NUMBER
%import common.SIGNED_NUMBER -> SIGNED_NUMBER
%import common.ESCAPED_STRING -> STRING
%import common.WS -> SPACE
"""

openwith = """
<FTL>
    <weaponBlueprint name="GB_AC_1_ELITE">
        <flavorType>Autocannon</flavorType>
        <tip>rvs_tip_autocannon</tip>
        <type>LASER</type>
        <title>Elite Autocannon Mark I</title>
        <short>€ AC I</short>
        <desc>The very basic ballistic weapon used by the Federation during the Federation-Mantis war. Heavily outdated by modern standards, it is still a weapon by all means.</desc>
        <tooltip>1 shot 1 damage weapon, 85% chance to not use ammo, 10% chance to cause a breach</tooltip>
        <missiles>1</missiles>
        <freeMissileChance>90</freeMissileChance> <!-- R4: Standard is 85 -->
        <damage>1</damage>
        <persDamage>1</persDamage>
        <shots>1</shots>
        <sp>0</sp>
        <breachChance>2</breachChance> <!-- R4: Standard is 1-->
        <cooldown>6</cooldown>
        <power>1</power>
        <stun>2</stun> <!-- R4: Gave elite AC 1 stun -->
        <bp>4</bp>
        <rarity>0</rarity>
        <cost>30</cost> <!-- R4: Standard is 20-->
        <image>GB_shot_light</image>
        <launchSounds>
            <sound>GB_cannonLight1</sound>
            <sound>GB_cannonLight2</sound>
            <sound>GB_cannonLight3</sound>
        </launchSounds>
        <hitShipSounds>
            <sound>hitHull2</sound>
            <sound>hitHull3</sound>
        </hitShipSounds>
        <hitShieldSounds>
            <sound>hitShield1</sound>
            <sound>hitShield2</sound>
            <sound>hitShield3</sound>
        </hitShieldSounds>
        <missSounds>
            <sound>miss</sound>
        </missSounds>
        <weaponArt>GB_Autocannon_1_Elite</weaponArt>
        <iconImage>laser</iconImage>
    </weaponBlueprint>
</FTL>

"""
