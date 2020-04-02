function selected()
    local panel = _G.module_ui
    local env = LuaScript.getEnvironment(this.universe.value, panel._entity, 0)
    env.setModule(this._entity)
end