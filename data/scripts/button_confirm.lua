progress_ui = {}
Editor.setPropertyType(this, "progress_ui", Editor.ENTITY_PROPERTY)

local progress = -1

function onRectMouseDown()
    progress = 0
end

function onRectHoveredOut()
    if progress >= 0 then
        progress_ui.gui_rect.right_relative = 0
        progress = -1
    end
end

function onInputEvent(event)
    if progress < 0 then return end
    if event.device.type ~= LumixAPI.INPUT_DEVICE_MOUSE then return end

    if event.type == LumixAPI.INPUT_EVENT_BUTTON then
        if not event.down then
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
        progress = progress + td * 3
        if progress > 1 then
            progress = -1
            progress_ui.gui_rect.right_relative = 0
            onConfirm()
            return
        end
        progress_ui.gui_rect.right_relative = progress
    end
end