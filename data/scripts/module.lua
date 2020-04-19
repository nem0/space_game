function selected()
    local panel = _G.module_ui
    local env = panel.lua_script[0]
    env.setModule(this)
end