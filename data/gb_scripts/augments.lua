local vter = mods.inferno.vter

-- Since none of the stuff is exposed to actually check how many missiles a weapon uses,
-- we have to read the blueprints and make our own list to reference
local ammoWeapons = nil
script.on_internal_event(Defines.InternalEvents.MAIN_MENU, function()
    log("MAIN MENU")
    if not ammoWeapons then
        log("COLLECTING AMMO WEAPONS")
        ammoWeapons = {}
        local function read_blueprint_file(file)
            local blueprintNode = RapidXML.xml_document(file):first_node("FTL"):first_node("weaponBlueprint")
            while blueprintNode do
                local missilesNode = blueprintNode:first_node("missiles")
                if missilesNode then
                    local numMissiles = tonumber(missilesNode:value())
                    if numMissiles and numMissiles > 0 then
                        ammoWeapons[blueprintNode:first_attribute("name"):value()] = numMissiles
                    end
                end
                blueprintNode = blueprintNode:next_sibling("weaponBlueprint")
            end
        end
        read_blueprint_file("data/blueprints.xml")
        read_blueprint_file("data/dlcBlueprints.xml")
    end
end)

-- Force ships with integrated ballistics to only use one non-ballistic weapon
local function handle_integrated_ballistics(weapons, ship)
    local firstAmmoWeaponFound = false
    for weapon in vter(weapons) do
        if weapon.powered and ammoWeapons and not ammoWeapons[weapon.blueprint.name] then
            if firstAmmoWeaponFound then
                weapon.cooldown.first = 0
                weapon.chargeLevel = 0
            else
                firstAmmoWeaponFound = true
            end
        end
    end
end
script.on_internal_event(Defines.InternalEvents.ON_TICK, function()
    local weaponsPlayer = nil
    if pcall(function() weaponsPlayer = Hyperspace.ships.player.weaponSystem.weapons end) and weaponsPlayer and Hyperspace.ships.player:HasAugmentation("GB_INTEGRATED_BALLISTICS") > 0 then
        handle_integrated_ballistics(weaponsPlayer, Hyperspace.ships.player)
    end
    local weaponsEnemy = nil
    if pcall(function() weaponsEnemy = Hyperspace.ships.enemy.weaponSystem.weapons end) and weaponsEnemy and Hyperspace.ships.enemy:HasAugmentation("GB_INTEGRATED_BALLISTICS") > 0 then
        handle_integrated_ballistics(weaponsEnemy, Hyperspace.ships.enemy)
    end
end)

-- Integrated ballistics provides a stackable 15% ammo replication chance
script.on_internal_event(Defines.InternalEvents.GET_AUGMENTATION_VALUE, function(shipManager, augName, augValue)
    if augName == "EXPLOSIVE_REPLICATOR" and shipManager:HasAugmentation("GB_INTEGRATED_BALLISTICS") > 0 then
        augValue = augValue + 0.15
    end
    return Defines.Chain.CONTINUE, augValue
end)
