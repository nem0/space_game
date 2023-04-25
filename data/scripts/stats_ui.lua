local props = { "power", "heat", "air", "water", "food" }
local units = { "kJ/s", "kJ/s", "l/h", "l/day", "kcal/day" }
local _ENV = getfenv()
for _, p in ipairs(props) do
    _ENV[p] = -1
    Editor.setPropertyType(this, p, Editor.ENTITY_PROPERTY)
end

function start()
    for _, p in ipairs(props) do
        local s = Lumix.Entity:new(this._world, _ENV[p])
        _ENV[p .. "_ui"] = s:getComponent("gui_text") 
    end
end

function update()
    local s = Game.getStationStats()
    for i, v in ipairs(props) do
        _ENV[v .. "_ui"].text = tostring(s[v.. "_prod"] - s[v .. "_cons"]) .. " " .. units[i] .. " (" .. tostring(s[v.. "_prod"]) .. " - " .. tostring(s[v.. "_cons"]) .. ")"
    end
end
