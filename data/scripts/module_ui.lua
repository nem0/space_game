values_container_ui = -1
Editor.setPropertyType(this, "values_container_ui", Editor.ENTITY_PROPERTY) 

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
    
    if v.update ~= nil then
        local s = e:createComponent("lua_script")
        local lua_scene = LumixAPI.getScene(this._universe, "lua_script")
        LuaScript.addScript(lua_scene, e._entity, 0)
        local evt = LuaScript.getEnvironment(this._universe, e._entity, 0)
        evt.update = function()
            v.update(e)
        end
        LuaScript.rescan(this._universe, e._entity, 0)
    end

    for k, c in ipairs(v) do
        c.parent = e
    end
    return e
end

function ui_text(t)
    local e = ui_rect(t)
    local ui_text = e:createComponent("gui_text")
    ui_text.text = t.text
    ui_text.font = "editor/fonts/opensans-bold.ttf"
    ui_text.font_size = t.font_size or 20
    ui_text.horizontal_align = t.horizontal_align or 0
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
        LuaScript.addScript(lua_scene, e._entity, 0)
        local evt = LuaScript.getEnvironment(this._universe, e._entity, 0)
        evt.onButtonClicked = function()
            v.on_click(e)
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
    button_color = {1, 1, 1, 1},
    dialog_bg_color = {1, 1, 1, 1},
    button_hovered_color = {1, 1, 1, 0.5}
}

function add_extension_button(v)
    return ui_button { 
        color = style.button_color,
        hovered_color = style.button_hovered_color,
        ui_text { text = v.title }
    }
end


function add_extension_popup(container)
    ui_img {
        color = {1, 1, 1, 1},
        top_relative = 1,
        bottom_points = 300,
        right_points = 100,
        parent = container,
        vlayout {
            left_points = 5,
            row_height = 30,
            row_spacing = 5,
            add_extension_button { title = "Air recycler", value = "air_recycler" },
            add_extension_button { title = "Hydroponics", value = "hydroponics" },
            add_extension_button { title = "Sleeping quarter", value = "sleeping_quarter" },
            add_extension_button { title = "Toilet", value = "toilet" },
            add_extension_button { title = "Water recycler", value = "water_recycler" },
        }
    }
end

function getExtensionByID(module_entity, id)
    local m = Game.getModule(module_entity)
    for _, e in ipairs(m.extensions) do
        if e.id == id then return e end
    end
    return nil
end

function ui_ext_assign_builder(ext, module)
    local builder = getBuilder(ext)
    if builder == nil and ext.build_progress < 1 then
        return ui_button {
            top_points = 10,
            left_relative = 1,
            left_points = -100,
            color = { 0.5, 0.5, 0.5, 1 },
            hovered_color = { 0.5, 0.5, 0.5, 0.5 },
            on_click = function(this)
                crew_popup(this, function(c)
                    refresh = module.entity
                    Game.assignBuilder(ext.id, c.id)
                end)
            end,
            ui_text {
                horizontal_align = 1,
                text = "Assign",
                font_size = 20
            }
        }
    end

    if builder ~= nil then
        return ui_text {
            text = builder.name .. " building...",
            font_size = 20,
            horizontal_align = 2,
            ui_img {
                color = {0, 1, 0, 1},
                update = function(this)
                    local p = getExtensionByID(module.entity, ext.id).build_progress
                    this:getComponent("gui_rect").right_relative = p
                    if p >= 1 then refresh = module.entity end
                end
            }
        }
    end
end

function ui_extension(v)
    return ui_rect {
        top_points = 5,
        bottom_points = 80, 
        bottom_relative = 0,
        ui_img {
            color = {0, 0, 0, 1},
            right_points = 40, 
            right_relative = 0, 
            bottom_points = 40, 
            bottom_relative = 0,
            ui_img {
                sprite = v.sprite, 
            }
        },
        ui_text {
            left_points = 45,
            text = v.text,
            font_size = 20,
            horizontal_align = 0
        },
        ui_ext_assign_builder(v.extension, v.module)
    }
end

function update()
    if refresh ~= -1 then
        setModule(refresh)
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

function setModule(entity)
    this:getComponent("gui_rect").enabled = true
    local m = Game.getModule(entity)

    local cont = Lumix.Entity:new(this._universe, values_container_ui)
    local c = cont.first_child 
    while c ~= nil do
        destroyHierarchy(c)
        c = cont.first_child 
    end

    if m.build_progress < 1 then 
        local crew = Game.getCrew()
        local ui = {
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
            parent = { _entity = values_container_ui },
            vlayout(ui),
            ui_img {
                top_relative = 1,
                top_points = -40,
                bottom_points = -5,
                ui_img {
                    right_relative = m.build_progress,
                    color = {0, 1, 0, 1},
                    update = function(this)
                        m = Game.getModule(m.entity)
                        this:getComponent("gui_rect").right_relative = m.build_progress
                        if m.build_progress >= 1 then
                            refresh = m.entity
                        end
                    end
                }
            }
        }
    else 
        local uis = join({
            parent = { _entity = values_container_ui },
            row_height = 40,
            row_spacing = 5,
            top_points = 5
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
            end
            
            return ui_text { text = "unknown"}
        end))

        table.insert(uis, ui_button {
            color = { 0.5, 0.5, 0.5, 1 },
            hovered_color = { 0.5, 0.5, 0.5, 0.5 },
            left_relative = 0.5,
            right_relative = 0.5,
            left_points = -75,
            right_points = 75,
            on_click = function(this)
                add_extension_popup(this, function(c)
                    refresh = m.entity
                end)
            end,
            ui_text {
                top_points = 5,
                text = "Add extension",
                font_size = 20,
                horizontal_align = 1
            }
        })

        vlayout(uis)
    end
end