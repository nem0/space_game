horizontal_sizer = {}
vertical_sizer = {}
sizer = {}
titlebar = {}
Editor.setPropertyType(this, "horizontal_sizer", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "vertical_sizer", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "sizer", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "titlebar", Editor.ENTITY_PROPERTY)

local drag_type = ""
local drag_start_value = {}
local drag_start_mp = {}
local mouse_in = false

function onRectHoveredOut()
    Gui.setCursor(0)
    mouse_in = false
end

function onRectHovered()
    Gui.setCursor(0)
    mouse_in = true
end

function onInputEvent(event)
    if event.device.type ~= LumixAPI.INPUT_DEVICE_MOUSE then return end

    if event.type == LumixAPI.INPUT_EVENT_BUTTON then
        if not event.down then
            drag_type = ""
        end
    elseif event.type == LumixAPI.INPUT_EVENT_AXIS then
        local gui_scene = this.universe:getScene("gui")
        local e = gui_scene:getRectAt({event.x_abs, event.y_abs})
            
        if e._entity ~= nil then
            if e._entity == horizontal_sizer._entity then
                Gui.setCursor(2)
            elseif e._entity == vertical_sizer._entity then
                Gui.setCursor(1)
            elseif e._entity == sizer._entity then
                Gui.setCursor(3)
            elseif mouse_in then
                Gui.setCursor(0)
            end
        end
        
        if drag_type == "" then return end
        local r = this.gui_rect
        local dx = event.x_abs - drag_start_mp.x
        local dy = event.y_abs - drag_start_mp.y

        if drag_type == "move" then
            r.right_points = drag_start_value.right + dx
            r.bottom_points = drag_start_value.bottom + dy
            r.left_points = drag_start_value.left + dx
            r.top_points = drag_start_value.top + dy
        elseif drag_type == "h_resize" then
            r.right_points = drag_start_value.right + dx
        elseif drag_type == "v_resize" then
            r.bottom_points = drag_start_value.bottom + dy
        elseif drag_type == "resize" then
            r.right_points = drag_start_value.right + dx
            r.bottom_points = drag_start_value.bottom + dy
        end
    end
end


function onRectMouseDown(x, y)
    dragged = true
    drag_start_mp = {x = x, y = y}
    local r = this.gui_rect
    drag_start_value.right = r.right_points 
    drag_start_value.bottom = r.bottom_points 
    drag_start_value.top = r.top_points 
    drag_start_value.left = r.left_points 
    
    local gui_scene = this.universe:getScene("gui")
    local e = gui_scene:getRectAt({x, y})
    if e == nil then return end

    if e._entity == horizontal_sizer._entity then
        drag_type = "h_resize"
    elseif e._entity == vertical_sizer._entity then
        drag_type = "v_resize"
    elseif e._entity == sizer._entity then
        drag_type = "resize"
    elseif e._entity == titlebar._entity then
        drag_type = "move"
    end
end