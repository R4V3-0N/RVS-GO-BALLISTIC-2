local vter = mods.inferno.vter

-- Force ships with integrated ballistics to only use one non-ballistic weapon
local function handle_integrated_ballistics(weapons, ship)
    local firstAmmoWeaponFound = false
    for weapon in vter(weapons) do
        if weapon.powered and weapon.blueprint.missiles > 0 then
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
