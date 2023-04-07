if not (Hyperspace.version and Hyperspace.version.major == 1 and Hyperspace.version.minor >= 3) then
    error("Incorrect Hyperspace version detected! Go Ballistic requires Hyperspace 1.3+")
end
if not mods or not mods.inferno then
    error("Couldn't find Inferno Core! Make sure it's above mods which depend on it in the Slipstream load order")
end
