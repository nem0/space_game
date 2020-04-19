default_pane = {}
assign_pane = {}
build_ext_pane = {}
build_ext_pane_back = {}
assign_pane_back = {}
build_ext_prefab = -1
ext_prefab = -1
ext_list = {}
build_ext_list = {}
assign_list = {}
module_assign_list = {}
switch_to_build_ext_pane = {}
build_module_pane = {}
assign_module_builder_button = {}
buile_module_progress = {}
free_space = {}
Editor.setPropertyType(this, "buile_module_progress", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "module_assign_list", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "assign_module_builder_button", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "build_module_pane", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "build_ext_list", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "assign_list", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "ext_list", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "default_pane", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "assign_pane", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "build_ext_pane", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "build_ext_prefab", Editor.RESOURCE_PROPERTY, "prefab") 
Editor.setPropertyType(this, "ext_prefab", Editor.RESOURCE_PROPERTY, "prefab") 
Editor.setPropertyType(this, "switch_to_build_ext_pane", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "build_ext_pane_back", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "assign_pane_back", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "free_space", Editor.ENTITY_PROPERTY) 

_G.module_ui = this
local refresh = -1
local selected_module = nil
local building = false

function ui_rect(v)
    local e = this.universe:createEntity()
    if v.parent ~= nil then
        e.parent = v.parent 
    end
    local ui_rect = e:createComponent("gui_rect")
    ui_rect.left_points = v.left_points or 0
    ui_rect.left_relative = v.left_relative or 0
    ui_rect.right_points = v.right_points or 0
    ui_rect.right_relative = v.right_relative or 1
    ui_rect.bottom_points = v.bottom_points or 0
    ui_rect.bottom_relative = v.bottom_relative or 1
    ui_rect.top_points = v.top_points or 0
    ui_rect.top_relative = v.top_relative or 0
    
    if v.update ~= nil then
        local s = e:createComponent("lua_script")
        local lua_scene = LumixAPI.getScene(this._universe, "lua_script")
        LuaScript.addScript(lua_scene, e, 0)
        local evt = e.lua_script[0]
        evt.update = function()
            v.update(e)
        end
        LuaScript.rescan(this._universe, e, 0)
    end

    for i = #v, 1, -1 do
        v[i].parent = e
    end
    return e
end

function ui_text(t)
    local e = ui_rect(t)
    local ui_text = e:createComponent("gui_text")
    ui_text.text = t.text
    ui_text.font = "fonts/gotham_rounded_medium.ttf"
    ui_text.font_size = t.font_size or 20
    ui_text.horizontal_align = t.horizontal_align or 0
    ui_text.vertical_align = t.vertical_align or 0
    return e
end

function ui_img(v)
    local e = ui_rect(v)
    local ui_img = e:createComponent("gui_image")
    ui_img.sprite = v.sprite or ""
    ui_img.color = v.color or {1, 1, 1, 1}
    return e
end

function ui_button(v)
    local e = ui_img(v)
    local ui_btn = e:createComponent("gui_button")
    ui_btn.hovered_color = v.hovered_color or {1, 1, 1, 1}

    if v.on_click ~= nil then
        e:createComponent("lua_script")
        local lua_scene = LumixAPI.getScene(this._universe, "lua_script")
        LuaScript.addScript(lua_scene, e, 0)
        local evt = e.lua_script[0]
        evt.onButtonClicked = function()
            v.on_click(e)
        end
    end
    return e
end

function grid(v)
    local e = ui_rect(v)
    local cols = v.cols
    local y = 0
    local col = 0
    local col_spacing = v.col_spacing or 5

    for _, c in ipairs(v) do
        local r = c.gui_rect
        r.left_relative = col / cols
        r.left_points = col_spacing * 0.5
        r.right_points = -col_spacing * 0.5
        r.right_relative = (col + 1) / cols
        r.bottom_relative = 0
        r.top_points = y
        r.bottom_points = y + v.row_height
        col = col + 1
        if col == cols then
            y = y + v.row_height + v.row_spacing
            col = 0
        end
    end

    return e
end

function vlayout(v)
    local e = ui_rect(v)

    local y = 0
    for _, c in ipairs(v) do
        local r = c:getComponent("gui_rect")
        r.bottom_relative = 0
        r.top_points = y
        r.bottom_points = y + v.row_height
        y = y + v.row_height + v.row_spacing
    end

    return e
end

function destroyHierarchy(e)
    while e.first_child ~= nil do 
        destroyHierarchy(e.first_child)
    end
    e:destroy()
end

function getBuilder(ext) 
    local crew = Game.getCrew()
    for _, c in ipairs(crew) do
        if c.state == "building" and c.subject == ext.id then return c end
    end
    return nil
end

function map(ar, fn)
    local res = {}
    for _, v in ipairs(ar) do
        table.insert(res, fn(v))
    end
    return res
end

function join(a, b)
    for _, v in ipairs(b) do
        table.insert(a, v)
    end
    return a
end

function crew_popup(container, callback)
    local crew = Game.getCrew()
    ui_img {
        top_relative = 1,
        bottom_points = 200,
        right_relative = 0,
        right_points = 300,
        parent = container,
        color = {1, 1, 1, 0.75},
        vlayout(join(
            { 
                row_height = 20,
                row_spacing = 5
            }, 
            map(crew, function(c) 
                return ui_button {
                    on_click = function()
                        callback(c)
                    end,
                    ui_text { text = c.name, font_size = 20, left_points = 5 }
                }
            end
        )))
    }
end

local style = {
    button_color = {1, 0.5, 0, 1},
    dialog_bg_color = {1, 1, 1, 1},
    button_hovered_color = {0.75, 0.75, 0.75, 0.5}
}

function slide_in_pane(pane)
    pane.gui_rect.enabled = true
    pane.lua_script[0].startSlide(1, 0)
end

function slide_out_pane(pane)
    pane.gui_rect.enabled = true
    pane.lua_script[0].startSlide(0, -1)
end

function enable_assign_pane(module, extension)
    slide_in_pane(assign_pane)

    local crew = Game.getCrew()

    destroyChildren(assign_list)

    for i, c in ipairs(crew) do
        row = math.floor((i - 1) / 3)
        col = math.floor((i - 1) % 3)
        ui_button {
            color = {1, 1, 1, 0.5},
            top_points = row * 50,
            bottom_points = row * 50 + 45,
            top_relative = 0,
            bottom_relative = 0,
            parent = assign_list,
            left_relative = col * 0.333,
            right_relative = col * 0.333 + 0.333,
            left_points = 5,
            on_click = function()
                slide_out_pane(assign_pane)
                if extension ~= nil then
                    refresh = module.entity
                    Game.assignBuilder(extension.id, c.id)
                    slide_in_pane(default_pane)
                else
                    refresh = module.entity
                    Game.assignBuilder(module.id, c.id)
                    slide_in_pane(build_module_pane)
                end
            end,
            ui_text {
                text = c.name,
                font_size = 20,
                vertical_align = 1,
                horizontal_align = 1
            }
        }
    end

end

function enable_build_pane(module)
    slide_in_pane(build_ext_pane)
    slide_out_pane(default_pane)
    
    while build_ext_list.first_child ~= nil do
        destroyHierarchy(build_ext_list.first_child)
    end

    local extensions = {
        { name = "Toilet", value = "toilet", icon = "ui/toilet.spr", desc = 
[[It's used to dispose of urine and excrements.
The waste is stored, so it can be recycled later.
It consumes 5 kJ/s of electricity.]]
},
        { name = "Air recycler", value = "air_recycler" , icon = "ui/air.spr", desc = 
[[Basic air recycler. It removes carbon dioxide from air and adds oxygen.
It consumes 25 kJ/s of electricity.]]   },
{ name = "Water recycler", value = "water_recycler", icon = "ui/water.spr", desc = 
[[Basic water recycler recycles all kinds of waste water, including urine.
It produces drinkable water and needs 25 kJ/s of electricity to do so.]]  },
    { name = "Sleeping quarter", value = "sleeping_quarter", icon = "ui/bed.spr", desc = 
    [[A place for one crewmember to sleep. 
While people can sleep even without sleeping quarter, 
it lower their health and morale considerably.]]  },
{ name = "Hydroponics", value = "hydroponics", icon = "ui/food.spr", desc = 
[[A method of growing plants without soil, 
by instead using mineral nutrient solutions in a water solvent.
It consumes 10 kJ/s of electricity and 5l/day of water.
It produces 20 000 kcal/day of food.]]  }
}

    for i, v in ipairs(extensions) do
        local e = LumixAPI.instantiatePrefab(this.universe, {0, 0, 0}, build_ext_prefab)
        e.parent = build_ext_list
        e.gui_rect.top_points = (i - 1) * 105
        e.gui_rect.bottom_points = i * 105 - 5

        local env = e.lua_script[0]
        v.clicked = function()
            slide_out_pane(build_ext_pane)
            slide_in_pane(default_pane)
            Game.onGUIEvent("build_" .. v.value)
            refresh = module.entity
        end
        env.set(module, v)
    end

    build_ext_list.gui_rect.bottom_points = #extensions * 105
end

function update_build_progress()
    if selected_module == nil then return end
    local m = Game.getModule(selected_module)
    if m == nil then return end
    buile_module_progress.gui_rect.right_relative = math.min(m.build_progress, 1)
    if m.build_progress >= 1 and building == true then 
        setModule(selected_module)
    end
end

function update()
    if refresh ~= -1 then
        setModule({_entity = refresh})
        refresh = -1
    end

    update_build_progress()

end

function getFreeSpace(module)
    local res = 60
    for _, e in ipairs(module.extensions) do
        if e.type == "air_recycler" then
            res = res - 12;
        elseif e.type == "water_recycler" then
            res = res - 15;
        elseif e.type == "toilet" then
            res = res - 20;
        elseif e.type == "sleeping_quarter" then
            res = res - 7;
        elseif e.type == "hydroponics" then
            res = res - 45;
        end
    end
    return res
end

function start()
    build_ext_pane.gui_rect.enabled = false
    assign_pane.gui_rect.enabled = false
    build_ext_pane_back.lua_script[0].onButtonClicked = function()
        slide_out_pane(build_ext_pane)
        slide_in_pane(default_pane)
    end
end

function destroyChildren(e)
    local c = e.first_child 
    while c ~= nil do
        destroyHierarchy(c)
        c = e.first_child 
    end
end

function setModule(entity)
    default_pane.gui_rect.enabled = true
    this.gui_rect.enabled = true
    build_module_pane.gui_rect.enabled = false

    local m = Game.getModule(entity)
    selected_module = entity

    local env = switch_to_build_ext_pane.lua_script[0]
    env.onButtonClicked = function()
        enable_build_pane(m)
    end

    destroyChildren(ext_list)

    building = m.build_progress < 1
    if m.build_progress < 1 then 
        build_module_pane.gui_rect.enabled = true
        default_pane.gui_rect.enabled = false
        build_ext_pane.gui_rect.enabled = false

        assign_module_builder_button.lua_script[0].onButtonClicked = function()
            assign_pane_back.lua_script[0].onButtonClicked = function()
                slide_out_pane(assign_pane)
                slide_in_pane(build_module_pane)
            end
            enable_assign_pane(m)
            slide_out_pane(build_module_pane)
        end

        local crew = Game.getCrew()

        destroyChildren(module_assign_list)
        buile_module_progress.gui_rect.enabled = true
        buile_module_progress.gui_rect.right_relative = math.max(0, m.build_progress)
        
        local i = 0
        for _, c in ipairs(crew) do
            if c.subject == m.id then
                row = math.floor(i / 3)
                col = i % 3
                ui_button {
                    color = {1, 1, 1, 0.5},
                    top_points = row * 50,
                    bottom_points = row * 50 + 45,
                    top_relative = 0,
                    bottom_relative = 0,
                    left_relative = col * 0.333,
                    right_relative = col * 0.333 + 0.333,
                    left_points = 5,
                    right_points = -5,
                    parent = module_assign_list,
                    on_click = function()
                        Game.assignBuilder(m.id, c.id)
                    end,
                    ui_text {
                        text = c.name,
                        font_size = 20,
                        vertical_align = 1,
                        horizontal_align = 1
                    }
                }
                i = i + 1
            end
        end
    else 
        local s = getFreeSpace(m)
        free_space.gui_text.text = tostring(s) .. "/ 60"
        for idx, ext in ipairs(m.extensions) do
            local e = LumixAPI.instantiatePrefab(this.universe, {0, 0, 0}, ext_prefab)
            local r = e.gui_rect
            local i = idx - 1
            local l = (i % 2) * 0.5
            e.parent = ext_list
            r.left_relative = l
            r.right_relative = l + 0.5
            r.top_points = math.floor(i / 2) * 80 + 5
            r.bottom_points = r.top_points + 75
            e.lua_script[0].set(m, ext)
        end
    end
end