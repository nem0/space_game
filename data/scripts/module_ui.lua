values_container_ui = {}
build_ext_pane = {}
Editor.setPropertyType(this, "values_container_ui", Editor.ENTITY_PROPERTY) 
Editor.setPropertyType(this, "build_ext_pane", Editor.ENTITY_PROPERTY) 

_G.module_ui = this
local refresh = -1


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
    
    if v.scripts~= nil then
        local s = e:createComponent("lua_script")
        local lua_scene = LumixAPI.getScene(this._universe, "lua_script")
        
    end

    if v.update ~= nil then
        local s = e:createComponent("lua_script")
        local lua_scene = LumixAPI.getScene(this._universe, "lua_script")
        LuaScript.addScript(lua_scene, e, 0)
        local evt = LuaScript.getEnvironment(this._universe, e, 0)
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
    ui_btn.normal_color = v.color or {1, 1, 1, 1}

    if v.on_click ~= nil then
        local s = e:createComponent("lua_script")
        local lua_scene = LumixAPI.getScene(this._universe, "lua_script")
        LuaScript.addScript(lua_scene, e, 0)
        local evt = LuaScript.getEnvironment(this._universe, e, 0)
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

function add_extension_button(v)
    return ui_button { 
        color = style.button_color,
        hovered_color = style.button_hovered_color,
        on_click = function()
            Game.onGUIEvent("build_" .. v.value)
            refresh = v.module.entity
        end,
        ui_img { 
            sprite = v.icon,
            right_relative = 0,
            right_points = 30,
            left_poits = 5,
            color = {0, 0, 0, 1}
        },
        ui_text { left_points = 50, text = v.title, vertical_align = 1 }
    }
end


function add_extension_popup(container, module)
    ui_img {
        scripts = {
            "scripts/close_on_blur.lua"
        },
        color = {1, 1, 1, 0.75},
        bottom_relative = 0,
        top_points = -300,
        left_relative = 0.5,
        right_relative = 0.5,
        right_points = 150,
        left_points = -150,
        parent = container,
        vlayout {
            top_points = 5,
            left_points = 5,
            right_points = -5,
            row_height = 30,
            row_spacing = 5,
            add_extension_button { module = module, icon = "ui/air.spr", title = "Air recycler", value = "air_recycler" },
            add_extension_button { module = module, icon = "ui/air.spr", title = "Hydroponics", value = "hydroponics" },
            add_extension_button { module = module, icon = "ui/bed.spr", title = "Sleeping quarter", value = "sleeping_quarter" },
            add_extension_button { module = module, icon = "ui/toilet.spr", title = "Toilet", value = "toilet" },
            add_extension_button { module = module, icon = "ui/water.spr", title = "Water recycler", value = "water_recycler" },
        }
    }
end

function enable_ext_pane()
    build_ext_pane.gui_rect.enabled = true
    values_container_ui.gui_rect.enabled = false
end

function getExtensionByID(module_entity, id)
    local m = Game.getModule({_entity = module_entity})
    for _, e in ipairs(m.extensions) do
        if e.id == id then return e end
    end
    return nil
end

function ui_ext_assign_builder(ext, module)
    local builder = getBuilder(ext)
    if builder == nil and ext.build_progress < 1 then
        return ui_button {
            top_points = -30,
            top_relative = 1,
            color = style.button_color,
            hovered_color = style.button_hovered_color,
            on_click = function(this)
                crew_popup(this, function(c)
                    refresh = module.entity
                    Game.assignBuilder(ext.id, c.id)
                end)
            end,
            ui_text {
                horizontal_align = 1,
                vertical_align = 1,
                text = "Assign",
                font_size = 15
            }
        }
    end

    if builder ~= nil then
        return ui_img {
            top_relative = 1,
            bottom_relative = 1,
            top_points = -5,
            bottom_points = 0,
            color = {0, 1, 0, 1},
            update = function(this)
                local p = getExtensionByID(module.entity, ext.id).build_progress
                this:getComponent("gui_rect").right_relative = p
                if p >= 1 then refresh = module.entity end
            end
        }
    end
end

function ui_extension(v)
    return ui_img {
        color = {0, 0, 0, 0.5},
        top_points = 5,
        bottom_points = 80, 
        bottom_relative = 0,
        ui_img {
            color = {0, 0, 0, 1},
            right_points = 40, 
            right_relative = 0, 
            bottom_points = 40, 
            bottom_relative = 0,
            sprite = v.sprite, 
        },
        ui_text {
            right_points = -5,
            text = v.text,
            font_size = 20,
            horizontal_align = 2,
            vertical_align = 0
        },
        --ui_recycle_ext(v.extension, v.module)
        ui_ext_assign_builder(v.extension, v.module)
    }
end

function update()
    if refresh ~= -1 then
        setModule({_entity = refresh})
        refresh = -1
    end
end

function ui_assign_builder(module, crewmember)
    if crewmember.state == "idle" then
        return ui_button {
            color = { 0.5, 0.5, 0.5, 1 },
            hovered_color = { 0.5, 0.5, 0.5, 0.5 },
            left_relative = 1,
            left_points = -100,
            right_points = -5,
            top_points = 5,
            bottom_points = -5,
            on_click = function()
                Game.assignBuilder(module.id, crewmember.id)
                refresh = module.entity
            end,
            ui_text {
                text = "Assign",
                font_size = 20,
                horizontal_align = 1
            }
        }
    end

    return ui_text {
        horizontal_align = 2,
        right_points = -5,
        text = "Building...",
        font_size = 20
    }
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
        end
    end
    return res
end

function setModule(entity)
    values_container_ui.gui_rect.enabled = true
    build_ext_pane.gui_rect.enabled = false
    this:getComponent("gui_rect").enabled = true
    local m = Game.getModule(entity)

    local cont = values_container_ui
    local c = cont.first_child 
    while c ~= nil do
        destroyHierarchy(c)
        c = cont.first_child 
    end

    if m.build_progress < 1 then 
        local crew = Game.getCrew()
        local ui = {
            cols = 2,
            row_height = 40,
            row_spacing = 5,
            top_points = 5,
            left_points = 5,
            right_points = -5,
            bottom_points = -5,
        }
        for _, c in ipairs(crew) do
            local u = ui_img {
                ui_text {
                    left_points = 5,
                    text = c.name,
                    font_size = 20
                },
                ui_assign_builder(m, c)
            }
            table.insert(ui, u)
        end
        ui_rect {
            parent = values_container_ui,
            grid(ui),
            ui_img {
                top_relative = 1,
                top_points = -10,
                bottom_points = -5,
                right_relative = m.build_progress,
                color = {0, 1, 0, 1},
                update = function(this)
                    m = Game.getModule({_entity = m.entity})
                    this:getComponent("gui_rect").right_relative = m.build_progress
                    if m.build_progress >= 1 then
                        refresh = m.entity
                    end
                end
            }
        }
    else 
        local uis = join({
            row_height = 70,
            row_spacing = 5,
            cols = 2,
            top_points = 25,
        },
        map(m.extensions, function(e)
            if e.type == "solar_panel" then
                return ui_extension { sprite = "ui/solar_panel.spr", text = "Solar panel", extension = e, module = m }
            elseif e.type == "air_recycler" then
                return ui_extension { sprite = "ui/air.spr", text = "Air recycler", extension = e, module = m }
            elseif e.type == "toilet" then
                return ui_extension { sprite = "ui/toilet.spr", text = "Toilet", extension = e, module = m}
            elseif e.type == "sleeping_quarter" then
                return ui_extension { sprite = "ui/bed.spr", text = "Sleeping quarter", extension = e, module = m }
            elseif e.type == "water_recycler" then
                return ui_extension { sprite = "ui/water.spr", text = "Water recycler", extension = e, module = m }
            end
        
            return ui_text { text = "unknown"}
        end))

        table.insert(uis, ui_button {
            color = { 1, 0.5, 0.0, 1 },
            hovered_color = { 0.5, 0.5, 0.5, 0.5 },
            on_click = function(this)
                enable_ext_pane()
            end,
            ui_img {
                sprite = "ui/build.spr",
                right_relative = 0,
                bottom_relative = 0,
                left_points = 5,
                top_points = 5,
                right_points = 45,
                bottom_points = 45,
                color = {0, 0, 0, 1}
            },
            ui_text {
                text = "Build extension",
                font_size = 20,
                right_points = -5,
                horizontal_align = 2,
                vertical_align = 0
            }
        })
        ui_rect {
            parent = values_container_ui,
            ui_text { text = "Free space: " .. tostring(getFreeSpace(m)) .. " / 60" },
            grid(uis)
        }
    end
end