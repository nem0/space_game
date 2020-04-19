vscrollbar = {}
content = {}
Editor.setPropertyType(this, "vscrollbar", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "content", Editor.ENTITY_PROPERTY)

local abs = 0
local scrolling = false

function start()
    local env = vscrollbar.lua_script[0]
    env.onRectMouseDown = function(x, y)
        scrolling = {y, abs}
    end

    local view_rect = Gui.getScreenRect(this)
    local content_rect = Gui.getScreenRect(content)
    local ratio = math.min(view_rect.h / content_rect.h, 1)
    vscrollbar.gui_rect.bottom_relative = ratio
    vscrollbar.gui_rect.top_relative = 0
    vscrollbar.gui_rect.top_points = 0
    vscrollbar.gui_rect.bottom_points = 0
end

function onInputEvent(event)
    if event.device.type ~= LumixAPI.INPUT_DEVICE_MOUSE then return end

    if event.type == LumixAPI.INPUT_EVENT_BUTTON then
        if not event.down then
            scrolling = false
        end
    end

    if event.type == LumixAPI.INPUT_EVENT_AXIS and scrolling ~= false then
        local start_mouse_y = scrolling[1]
        local start_abs = scrolling[2]

        local mouse_diff = event.y_abs - start_mouse_y
        
        local view_rect = Gui.getScreenRect(this)
        local scollbar_rect = Gui.getScreenRect(vscrollbar)
        local content_rect = Gui.getScreenRect(content)

        abs = start_abs + mouse_diff * content_rect.h / view_rect.h
        abs = math.min(abs, content_rect.h - view_rect.h)
        abs = math.max(0, abs)

        vscrollbar.gui_rect.top_relative = abs / content_rect.h
        vscrollbar.gui_rect.bottom_relative = (abs + view_rect.h) / content_rect.h

        content.gui_rect.top_points = -abs
        content.gui_rect.bottom_points = -abs + content_rect.h
    end
end
