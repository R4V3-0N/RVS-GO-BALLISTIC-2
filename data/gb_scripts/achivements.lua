----------------------
-- HELPER FUNCTIONS --
----------------------

local vter = mods.inferno.vter

local function is_first_shot(weapon, afterFirstShot)
    local shots = weapon.numShots
    if weapon.weaponVisual.iChargeLevels > 0 then shots = shots*(weapon.weaponVisual.boostLevel + 1) end
    if weapon.blueprint.miniProjectiles:size() > 0 then shots = shots*weapon.blueprint.miniProjectiles:size() end
    if afterFirstShot then shots = shots - 1 end
    return shots == weapon.queuedProjectiles:size()
end

local function userdata_table(userdata, tableName)
    if not userdata.table[tableName] then userdata.table[tableName] = {} end
    return userdata.table[tableName]
end

local function string_starts(str, start)
    return string.sub(str, 1, string.len(start)) == start
end

local function should_track_achievement(achievement, ship, shipClassName)
    return ship and
           Hyperspace.Global.GetInstance():GetCApp().world.bStartedGame and
           Hyperspace.CustomAchievementTracker.instance:GetAchievementStatus(achievement) < Hyperspace.Settings.difficulty and
           string_starts(ship.myBlueprint.blueprintName, shipClassName)
end

local function current_sector()
    return Hyperspace.Global.GetInstance():GetCApp().world.starMap.worldLevel + 1
end

local function count_ship_achievements(achPrefix)
    local count = 0
    for i = 1, 3 do
        if Hyperspace.CustomAchievementTracker.instance:GetAchievementStatus(achPrefix.."_"..tostring(i)) > -1 then
            count = count + 1
        end
    end
    return count
end

--------------------------
-- FEDERATION FREIGHTER --
--------------------------

-- Easy
local maxSpicesLastFrame = false
script.on_internal_event(Defines.InternalEvents.SHIP_LOOP, function(ship)
    if ship.iShipId == 0 and should_track_achievement("ACH_SHIP_RVSP_FED_FREIGHTER_1", ship, "PLAYER_SHIP_RVSP_FED_FREIGHTER") then
        local maxSpices = ship:HasEquipment("GB_EXOTIC_SPICES_9") > 0
        if Hyperspace.playerVariables.loc_ach_fedfreighter_deliveries >= 5 or (not maxSpices and maxSpicesLastFrame) then
            Hyperspace.CustomAchievementTracker.instance:SetAchievement("ACH_SHIP_RVSP_FED_FREIGHTER_1", false)
        end
        maxSpicesLastFrame = maxSpices
    end
end)

-- Normal
script.on_internal_event(Defines.InternalEvents.SHIP_LOOP, function(ship)
    if ship.iShipId == 0 and current_sector() < 3 and should_track_achievement("ACH_SHIP_RVSP_FED_FREIGHTER_2", ship, "PLAYER_SHIP_RVSP_FED_FREIGHTER") and ship:GetSystem(3):GetMaxPower() >= 6 then
        Hyperspace.CustomAchievementTracker.instance:SetAchievement("ACH_SHIP_RVSP_FED_FREIGHTER_2", false)
    end
end)

-- Hard
-- TODO: come up with and implement a hard achievement
