submenu = -1
Editor.setPropertyType(this, "submenu", Editor.ENTITY_PROPERTY)

function onButtonClicked()
    local s = Lumix.Entity:new(this._universe, submenu)
    local r = s:getComponent("gui_rect")
    r.enabled = not r.enabled
end