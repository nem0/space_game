local t = -1
local dst = -1
local src = -1
local rect = nil

function startSlide(from, to)
    src = from
    t = 0
    dst = to
    rect = this.gui_rect
    rect.left_relative = from
    rect.right_relative = from + 1
end

function update(td)
    if t >= 0 then
        t = t + td * 3
        if t > 1 then
            t = -1
            rect.left_relative = dst
            rect.right_relative = dst + 1
            return
        end
        local x = (1 - t) * src + t * dst
        rect.left_relative = x
        rect.right_relative = x + 1
    end
end