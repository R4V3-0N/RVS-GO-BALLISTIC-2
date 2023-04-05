if not mods or not mods.inferno then
    error("Couldn't find Inferno Core! Make sure it's above mods which depend on it in the Slipstream load order", 2)
end

-- Add ion damage for EMP weapons which only effects rooms
local empWeapons = {}
empWeapons["GB_AC_1_EMP"] = 1
empWeapons["GB_AC_2_EMP"] = 2
empWeapons["GB_AC_3_EMP"] = 3
empWeapons["GB_AC_2_ELITE_EMP"] = 1
empWeapons["GB_AC_3_ELITE_EMP"] = 2
script.on_internal_event(Defines.InternalEvents.DAMAGE_AREA_HIT, function(ship, projectile, damage, response)
    local empAmount = nil
    if pcall(function() empAmount = empWeapons[Hyperspace.Get_Projectile_Extend(projectile).name] end) and empAmount then
       local empHullHit = Hyperspace.Damage()
       empHullHit.iIonDamage = empAmount
       local weaponName = Hyperspace.Get_Projectile_Extend(projectile).name
       Hyperspace.Get_Projectile_Extend(projectile).name = ""
       ship:DamageArea(projectile.position, empHullHit, true)
       Hyperspace.Get_Projectile_Extend(projectile).name = weaponName
    end
end)
