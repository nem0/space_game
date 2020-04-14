progress_ui = {}
Editor.setPropertyType(this, "progress_ui", Editor.ENTITY_PROPERTY)

local mouse_inside = false
local progress = -1
function onRectHovered()
    mouse_inside = true
end
function onRectHoveredOut()
    mouse_inside = false
    if progress >= 0 then
        progress_ui.gui_rect.right_relative = 0
        progress = -1
    end
end

function onInputEvent(event)
    if not mouse_inside then return end
    if event.device.type ~= LumixAPI.INPUT_DEVICE_MOUSE then return end

    if event.type == LumixAPI.INPUT_EVENT_BUTTON then
        if event.down then
            progress = 0
        else
            progress_ui.gui_rect.right_relative = 0
            progress = -1
        end
    end
end

function start()
    progress_ui.gui_rect.right_relative = 0
end

function update(td)
    if progress >= 0 then
        progress = progress + td * 2
        if progress > 1 then
            progress = -1
            onButtonClicked()
            progress_ui.gui_rect.right_relative = 0
            return
        end
        progress_ui.gui_rect.right_relative = progress
    end
end