-- Add ion damage for EMP weapons which only effects rooms
local empWeapons = {}
empWeapons["GB_AC_1_EMP"] = 1
empWeapons["GB_AC_2_EMP"] = 2
empWeapons["GB_AC_3_EMP"] = 3
empWeapons["GB_AC_2_ELITE_EMP"] = 1
empWeapons["GB_AC_3_ELITE_EMP"] = 2
script.on_internal_event(Defines.InternalEvents.DAMAGE_AREA_HIT, function(ship, projectile, damage, response)
    local empAmount = nil
    if pcall(function() empAmount = empWeapons[projectile.extend.name] end) and empAmount then
       local empHullHit = Hyperspace.Damage()
       empHullHit.iIonDamage = empAmount
       local weaponName = projectile.extend.name
       projectile.extend.name = ""
       ship:DamageArea(projectile.position, empHullHit, true)
       projectile.extend.name = weaponName
    end
end)
