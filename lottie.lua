local M = class("LottieLayer", cc.Layer)

-- data = {
--     layers =
--     {
--         p =
--         {
--             {
--                 st = 0,
--                 t = 0,
--                 f = {100, 200},
--                 t = {200, 300},
--             },
--             {
--                 st = 0,
--                 t = 0,
--                 f = {100, 200},
--                 t = {200, 300},
--             },
--         },
--         texture = "",
--         showTime = 300,
--         hideTime = 400,
--         id = "",
--         parent = "",
--     },
-- }
function M:ctor(data)
    --将要显示的层信息
    self.mWillShowLayersInfo = {}
    self.mLayerInfoMap = {}
    
    local  rootLayers = {}
    self.mParentLayer = {}
    for i, v in ipairs(data.layers) do
        table.insert(self.mWillShowLayersInfo, v)
        self.mLayerInfoMap[v.id] = v
        
        if not v.parent then
            table.insert(rootLayers, v)
        else
            if not self.mParentLayer[v.parent] then
                self.mParentLayer[v.parent] = {}
            end
            table.insert(self.mParentLayer[v.parent], v)
        end
    end
    
    --已经显示的层信息
    self.mShowLayer = {}
    
    self.data = data
    self.mTime = 0;
    self:setContentSize(data.w, data.h)
    self:setPosition(data.x or 0, data.x or 0)
    
    for i, v in ipairs(rootLayers) do
        self:createLayer(v)
        self:createLayerByParentkey(v.id)
    end
end

function M:createLayerByParentkey(parent)
    if not self.mParentLayer[parent] then
        return
    end
    
    for i, v in ipairs(self.mParentLayer[parent]) do
        self:createLayer(v)
        self:createLayerByParentkey(v.id)
    end
end

function M:update(dt)
    self.mTime = dt + self.mTime;
    
    local removeLayers = {}
    local showLayers = {}

    for id, info in pairs(self.mLayerInfoMap) do
        if self.mShowLayer[info.id] then
            if info.st and  info.et and info.st <= self.mTime and info.et > self.mTime  then
                self.mShowLayer[info.id]:show()
            else
            self.mShowLayer[info.id]:hide()
            end
        end
    end
end

function M:createLayer(info)
    if self.mShowLayer[info.id] then
        return self.mShowLayer[info.id]
    end

    local node
    if info.texture then
        node = display.newSprite(info.texture)
    elseif info.module then
        node  = M:create(info.module)    
    else
        node = cc.Layer:create()
    end
    node:hide()
    --尺寸
    if info.w and info.h then
        node:setContentSize(info.w, info.h)
    end
    
    --坐标
    if info.x and info.y then
        node:setPosition(info.x, info.y)
    end
    
    --锚点
    if info.ax and info.ay then
        node:setIgnoreAnchorPointForPosition(false)
        node:setAnchorPoint(info.ax, info.ay)
    end
    
    --缩放
    if info.sx then
        node:setScaleX(info.sx)
    end
    
    if info.sy then
        node:setScaleY(info.sy)
    end
    
    --旋转
    if info.r then
        node:setRotation(info.r)
    end
    
    --设置父节点
    if info.parent then
        if self.mShowLayer[info.parent] then
            node:addTo(self.mShowLayer[info.parent])
        else
            -- local parentInfo = self.mLayerInfoMap[info.parent]
            error("can't run here")
        -- self:createLayer(parentInfo)
        -- node:addTo(self.mShowLayer[info.parent])
        end
    else
        node:addTo(self)
    end
    
    node.info = info;
    
    self.mShowLayer[info.id] = node;
    return node
end

function M:playNodeAnimation(node, startTime)
    local info = node.info;
    if not info then return end;
    
    --移动动画
    if info.pa then
        local actions = {}
        if info.st and info.st > 0 then 
            table.insert(actions, cc.DelayTime:create(info.st))
        end 
        local t = 0
        for i, v in ipairs(info.pa) do
            if v.st - t > 0 then
                table.insert(actions, cc.DelayTime:create(v.st - t))
            end
            t = v.st + v.t
            
            table.insert(actions, cc.MoveTo:create(0, cc.p(unpack(v.s))))
            table.insert(actions, cc.BezierTo:create(v.t, {cc.p(unpack(v.p1)), cc.p(unpack(v.p2)), cc.p(unpack(v.p3))}))
        end
        node:runAction(cc.Sequence:create(unpack(actions)))
    end
    
    --透明动画
    if info.oa then
        local actions = {}
        if info.st and info.st > 0 then 
            table.insert(actions, cc.DelayTime:create(info.st))
        end 
        local t = 0
        for i, v in ipairs(info.oa) do
            if v.st - t > 0 then
                table.insert(actions, cc.DelayTime:create(v.st - t))
            end
            t = v.st + v.t
            table.insert(actions, cc.FadeTo:create(v.t, v.e))
        end
        node:runAction(cc.Sequence:create(unpack(actions)))
    end
    
    --旋转动画
    if info.ra then
        
        local actions = {}
        if info.st and info.st > 0 then 
            table.insert(actions, cc.DelayTime:create(info.st))
        end 
        local t = 0
        for i, v in ipairs(info.ra) do
            if v.st - t > 0 then
                table.insert(actions, cc.DelayTime:create(v.st - t))
            end
            t = v.st + v.t
            table.insert(actions, cc.RotateTo:create(v.t, v.e))
        end
        node:runAction(cc.Sequence:create(unpack(actions)))
    
    end
    
    --缩放动画
    if info.sa then
        local actions = {}
        if info.st and info.st > 0 then 
            table.insert(actions, cc.DelayTime:create(info.st))
        end 
        local t = 0
        for i, v in ipairs(info.sa) do
            if v.st - t > 0 then
                table.insert(actions, cc.DelayTime:create(v.st - t))
            end
            t = v.st + v.t
            table.insert(actions, cc.ScaleTo:create(v.t, unpack(v.e)))
        end
        node:runAction(cc.Sequence:create(unpack(actions)))
    end
    
    if info.module then
        local action0 = cc.DelayTime:create(info.st)

        local action1 = cc.CallFunc:create(function()
            node:playAnimation(startTime)
            -- local moduleNode = M:create(info.module)
            -- -- dump(info.ax, info.ay)
            -- -- moduleNode:setAnchorPoint(info.ax, info.ay)
            -- -- moduleNode:setContentSize(info.w , info.h)
            -- moduleNode:addTo(node)
            -- moduleNode:playAnimation(startTime)
        end)
        node:runAction(cc.Sequence:create(action0, action1))
        node:setCascadeOpacityEnabled(true)
    end

end



function M:playAnimation(startTime)
    startTime = startTime or 0
    self:scheduleUpdateWithPriorityLua(function(dt)
        self:update(dt)
    end, 0)
    self:update(0)

    for i, node in pairs(self.mShowLayer) do
        self:playNodeAnimation(node, startTime)
    end 
end

return M;
