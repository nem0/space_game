function add(a, b)
    return {
        a[1] + b[1],
        a[2] + b[2],
        a[3] + b[3]
    }
end

function mul(f, v)
    return {
        f * v[1],
        f * v[2],
        f * v[3]
    }
end

function start()
    local center = { 0, -700, -700 }

    for i = 1, 1000 do
        local e = this.world:createEntity()
        local x = math.random() * 2 - 1
        local y = math.random() * 2 - 1
        e.position = add(add(center, mul(x, {2000, 0, 0})), mul(y, {0, -700, 700}))
        e.parent = this
        e.scale = 0.5 + math.random()
        local m = e:createComponent("model_instance")
        m.source = "models/star.fbx" 
    end
end