title = {}
icon = {}
assign_button = {}
build_progress = {}
Editor.setPropertyType(this, "title", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "icon", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "assign_button", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "build_progress", Editor.ENTITY_PROPERTY)

function getExtensionByID(module_entity, id)
    local m = Game.getModule({_entity = module_entity})
    for _, e in ipairs(m.extensions) do
        if e.id == id then return e end
    end
    return nil
end

local module = nil
local extension = nil

function set(m, v)
    module = m
    extension = v
    if v.type == "solar_panel" then
        title.gui_text.text = "Solar panel"
        icon.gui_image.sprite = "ui/solar_panel.spr"
    elseif v.type == "toilet" then
        title.gui_text.text = "Toilet"
        icon.gui_image.sprite = "ui/toilet.spr"
    elseif v.type == "air_recycler" then
        title.gui_text.text = "Air recycler"
        icon.gui_image.sprite = "ui/air.spr"
    elseif v.type == "water_recycler" then
        title.gui_text.text = "Water recycler"
        icon.gui_image.sprite = "ui/water.spr"
    elseif v.type == "sleeping_quarter" then
        title.gui_text.text = "Sleeping quarter"
        icon.gui_image.sprite = "ui/bed.spr"
    elseif v.type == "hydroponics" then
        title.gui_text.text = "Hydroponics"
        icon.gui_image.sprite = "ui/food.spr"
    else
        title.gui_text.text = "Unknown " .. v.type
    end
    assign_button.gui_rect.enabled = v.build_progress < 1 and v.builder == -1
    build_progress.gui_rect.enabled = v.builder ~= -1
    assign_button.lua_script[0].onButtonClicked = function()
        local env = _G.module_ui.lua_script[0]
        env.assign_pane_back.lua_script[0].onButtonClicked = function()
            env.slide_out_pane(env.assign_pane)
            env.slide_in_pane(env.default_pane)
        end
        env.enable_assign_pane(module, v)
        env.slide_out_pane(env.default_pane)
    end
end

function update()
    if module == nil then return end

    local ext = getExtensionByID(module.entity, extension.id)
    build_progress.gui_rect.enabled = ext.builder ~= -1
    local p = ext.build_progress
    if p >= 1 then return end
    
    build_progress.gui_rect.right_relative = math.max(0, p)
    assign_button.gui_rect.enabled = ext.builder == -1 and p < 1
end

