submenu = -1
Editor.setPropertyType(this, "submenu", Editor.ENTITY_PROPERTY)

function onButtonClicked()
    local r = submenu.gui_rect
    r.enabled = not r.enabled
end