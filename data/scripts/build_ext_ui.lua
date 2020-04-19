title = {}
icon = {}
desc = {}
button = {}
Editor.setPropertyType(this, "title", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "icon", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "desc", Editor.ENTITY_PROPERTY)
Editor.setPropertyType(this, "button", Editor.ENTITY_PROPERTY)

function set(module, v)
    title.gui_text.text = v.name
    desc.gui_text.text = v.desc
    icon.gui_image.sprite = v.icon
    local env = button.lua_script[0]
    env.onConfirm = function()
        v.clicked()
    end
end
