power = {}
heat  = {}
air  = {}
water  = {}
food  = {}
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
    power_ui = power.gui_text
    heat_ui = heat.gui_text
    air_ui = air.gui_text
    water_ui = water.gui_text
    food_ui = food.gui_text
end

function update()
    local s = Game.getStationStats()
    power_ui.text = tostring(s.power_prod - s.power_cons) .. " kJ/s"
    heat_ui.text = tostring(s.heat_prod - s.heat_cons) .. " kJ/s"
    air_ui.text = tostring(s.air_prod - s.air_cons) .. " l/h"
    water_ui.text = tostring(s.water_prod - s.water_cons) .. " l/day"
    food_ui.text = tostring(s.food_prod - s.food_cons) .. " kcal/day"
end
