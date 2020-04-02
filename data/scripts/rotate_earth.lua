local angle = 0
speed = 0.1
function update(time_delta)
    angle = angle + time_delta * speed
    local c = math.cos(angle * 0.5)
    local s = math.sin(angle * 0.5)
    this.rotation = { 0, s, 0, c }
end