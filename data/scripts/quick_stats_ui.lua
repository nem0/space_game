power = -1
heat  = -1
air  = -1
water  = -1
food  = -1
Editor.setPropertyType(this, "power", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "heat", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "air", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "water", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "food", Editor.ENTITY_PROPERTY)

local power_ui = 0
local heat_ui = 0
local air_ui = 0
local water_ui = 0
local food_ui = 0

function start()
    local s = Lumix.Entity:new(this._universe, power)
    power_ui = s:getComponent("gui_text")

    s = Lumix.Entity:new(this._universe, heat)
    heat_ui = s:getComponent("gui_text")

    s = Lumix.Entity:new(this._universe, air)
    air_ui = s:getComponent("gui_text")

    s = Lumix.Entity:new(this._universe, water)
    water_ui = s:getComponent("gui_text")

    s = Lumix.Entity:new(this._universe, food)
    food_ui = s:getComponent("gui_text")
end

function update()
    local s = Game.getStationStats()
    power_ui.text = tostring(s.power_prod - s.power_cons) .. " kJ/s"
    heat_ui.text = tostring(s.heat_prod - s.heat_cons) .. " kJ/s"
    air_ui.text = tostring(s.air_prod - s.air_cons) .. " l/h"
    water_ui.text = tostring(s.water_prod - s.water_cons) .. " l/day"
    food_ui.text = tostring(s.food_prod - s.food_cons) .. " kcal/day"
end
