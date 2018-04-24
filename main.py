
#-*-coding:utf-8-*-
from __future__ import division
import json
import uuid
import types


#==types.ts==
class Options:
    def createLayer(self, id, width, height):
        pass
    def createSprite(self,id, name, width, height):
        pass 
    def setPosition(self,id, x, y):
        pass 

    def animationAnimate(self,id,data, isSequence):
        pass

    def positionAnimate(self,id, data, delay, parentHeight):
        pass 
    def setAnchorPoint(self,id, x, y):
        pass 
    def setRotation(self,id, rotation):
        pass 
    def rotationAnimate(self,id, data, delay):
        pass 
    def setScale(self,id, x, y):
        pass 
    def scaleAnimate(self,id, data, delay):
        pass 
    def moveTo(self,id, parentId, time, x, y):
        pass 
    def setContentSize(self,id, width, height):
        pass 
    def addChild(self,id, parentId, localZOrder = None):
        pass 
    def getNode(self,id):
        pass 
    def setOpacity(self,id, opacity):
        pass 
    def fadeTo(self,id, data, delay):
        pass 

    def createDrawNode(self,id, parentId, width):
        pass 
    def drawCubicBezier(
    id,
    origin,
    c1,
    c2,
    dest,
    width,
    color,
    ):
        pass 
    def drawEllipse(self,id, *args):
        pass 
    def curveAnimate(self,id, width, color, config):
        pass 

class Layer:
    precomp = 0
    solid = 1
    image = 2
    null = 3
    shape = 4
    text = 5


class Shape:
    ellipse = 'el'
    group = 'gr'
    shape = 'sh'
    transform = 'tr'
    stroke = 'st'
    fill = 'fl'
    merge = 'mm'


class Effect:
    slider = 0
    angle = 1
    color = 2
    point = 3
    checkbox = 4
    group = 5
    dropDown = 7

#==traverse.ts==
getnIdKey = 0
def genId(nm = None):
    if nm is None:
        nm = "v"
    global getnIdKey
    getnIdKey = getnIdKey + 1  
    return nm + "_" + str(uuid.uuid3(uuid.NAMESPACE_OID,str(getnIdKey))).replace("-", "_")

def convertColor(c):
    return map(lambda n: n * 0xFF, c)


def isNum(d):
    return type(d) == types.FloatType or type(d) == types.IntType or type(d) == types.LongType
       
class Traverse:
    def __init__(self, data, containerId, useSpriteFrame, options):
        self.options = options
        self.assets = {}
        self.layers = {}
        self.data = data
        self.useSpriteFrame = useSpriteFrame
        self.rootWidth =  data["w"]
        self.rootHeight = data["h"]
        self.rootId = "root"
        
        #初使化asset
        for asset in data['assets']:
            if "id" in asset.keys():               
                self.assets[asset["id"]] = asset

        #初使化layer
        z = len(data["layers"])
        sortedLayers = {}
        for layer in data["layers"]:
            if "ind" in layer.keys():               
                self.layers[layer["ind"]] = layer   
                if "parent" not in layer:
                    if not self.rootId in sortedLayers.keys():
                         sortedLayers[self.rootId] = []
                    
                    sortedLayers[self.rootId].insert(0, layer)
                   
                else:
                    if not layer["parent"] in sortedLayers.keys():
                         sortedLayers[layer["parent"]] = []                    
                    if layer["parent"] == 0:
                        sortedLayers[layer["parent"]].insert(0, layer)
                    else:
                        sortedLayers[layer["parent"]].append(layer)
               
    
        self.layers[self.rootId] = {"w":self.rootWidth, "h": self.rootHeight, "z" :0}

        #创建root layer
        options.createLayer(self.rootId, data['w'], data['h'])
        
     
        self.__traverseLayer2(self.rootId, sortedLayers)

    def __traverseLayer2(self, rootId, sortedLayers):
        if rootId not in sortedLayers.keys():
            return 

        for layer in sortedLayers[rootId]:                      
            if "ind" not in layer.keys():
                continue
            self.__traverseLayer(layer, 0)
            self.__traverseLayer2(layer['ind'], sortedLayers)

    def __getTime(self, time):
        return time / self.data['fr']

    def getAsset(self, refId):
        if refId in self.assets.keys():
            return self.assets[refId]
        return None
    
    def getLayer(self, ind):
        if ind in self.layers.keys():
            return self.layers[ind]
        return None

    def __c(self, x, d, parentHeight):
        i,o,v = x["i"], x["o"],x["v"]
        d["data"] = []
        for j in range(len(v) - 1):
            d["data"].append(
                [

                { "x": v[j][0], "y": parentHeight - v[j][1] },
                { "x": v[j][0] + o[j][0], "y": parentHeight - v[j][1] - o[j][1] },
                {
                  "x": v[j + 1][0] + i[j + 1][0],
                  "y": parentHeight - v[j + 1][1] - i[j + 1][1],
                },
                { "x": v[j + 1][0], "y": parentHeight - v[j + 1][1] },
                ]
            )


    def __traverseShape(self, data, parentId, parentWidth, parentHeight,id = None, d = None):
        ty = data["ty"]
        options = self.options
        if ty == Shape.group:
            id = genId()
            d = {
                "id" :id,
                'stroke': None,
                'shape': [],
                'ellipse': None,
                'transform': None,
            }
            for item in data["it"]:
                self.__traverseShape(item, parentId, parentWidth, parentHeight, id, d)

            strokeWidth = None
            if d['stroke'] and 'width' in  d['stroke'].keys():
                strokeWidth = d['stroke']['width']
            options.createDrawNode(id, parentId, strokeWidth)

            for item in  d["shape"]:
                options.drawCubicBezier(id, item[0], item[1], item[2], item[3], d['stroke']['width'], d['stroke']['color'])

            if d['ellipse'] != None:
                x, y = d["transform"]['p']['k'][0], d["transform"]['p']['k'][1]
                rx, ry = d['ellipse']['s']['k'][0],d['ellipse']['s']['k'][1]
                center = { "x" : x, "y": -y }
                options.drawEllipse(id, center, rx, ry, 0, 100, True, d['stroke']['width'], d['stroke']['color'], d['fill']['color'])
        elif ty == Shape.stroke:
            if id != None:
                d["stroke"] ={
                    "width":data["w"]["k"],
                    "color":convertColor(data["c"]["k"])
                }
        elif ty == Shape.shape:
            if id == None or d == None   :
                return
            if "ks" in data.keys():
                if type(data["ks"]["k"]) == types.ListType:
                    self.__c(data["ks"]["k"][0]["s"][0], d, parentHeight)
                else:
                    self.__c(data["ks"]["k"], d, parentHeight)

        elif ty ==  Shape.transform:
            d['transform'] = data
        elif  ty ==  Shape.ellipse:
            d['ellipse'] = data
        elif  ty == Shape.fill:
            d["fill"]={
                "color": convertColor(data['c']['k']),
                "opacity": data['o']['k'],
            }
        elif ty == Shape.merge:
            pass 
        else :
            print "error in " + ty


    def __applyAnchor(self, layer, id, width, height):
        pass  


    def __parseK(self, k):
        ret =  {
          "nextTime": None,
          "arr": []
        }
        i = len(k)
        for item  in reversed(k):
            if "s" in  item.keys():
                startTime  = 0
                if i != 1:
                    startTime = self.__getTime(item["t"] )
                to = None
                if "to" in item.keys():
                    to = item['to']
                ti = None
                if "ti" in item.keys():
                    ti = item['ti']

                ret["arr"].insert(0, {
                    "s":item["s"],
                    'e':item['e'],
                    'to':to,
                    'ti':ti,
                     "t":self.__getTime( ret["nextTime"] - item["t"] ),
                     "startTime" :startTime
                })
            i = i -1

            ret["nextTime"] = item["t"]
        return ret




    def __applyTransform(self, layer, id,parentId,  width,    height,  parentWidth,    parentHeight,    st):
        options = self.options
              
        if not "ks" in layer.keys():
            return 
        
        if "o" in layer["ks"]:
            k = layer["ks"]["o"]["k"]
            if type(k) == types.ListType and  len(k) > 1:
                opacity = k[0]["s"][0]
                options.setOpacity(id, opacity * 2.55)
                ret = self.__parseK(k)
                options.fadeTo(id, ret['arr'], self.__getTime(st))
            elif isNum(k):
                options.setOpacity(id, k * 2.55)

        if "a" in layer["ks"]:
            k = layer["ks"]["a"]["k"]
            if type(k) == types.DictType and  "x" in k.keys():
                options.setAnchorPoint(id, k['x'] / width, 1 - k['y'] / height)
            else:
                if width != 0 and  height != 0:
                    options.setAnchorPoint(id, k[0] / width, 1 - k[1] / height)

        if "p" in layer["ks"]:
            k = layer["ks"]["p"]["k"]
            if type(k) ==  types.ListType and  isNum(k[0]):
                options.setPosition(id, k[0], parentHeight - k[1])
            elif type(k) ==  types.ListType and type(k[0]) == types.DictType:
                x, y = k[0]['s'][0],k[0]['s'][1]
                options.setPosition(id, x, parentHeight - y)
                ret = self.__parseK(k)
                options.positionAnimate(id, ret['arr'],self.__getTime(st), parentHeight)

        if "r" in layer["ks"]:
            k = layer["ks"]["r"]["k"]
            if isNum(k):
                options.setRotation(id, k)
            elif type(k) ==  types.ListType and isNum( k[0])  :
                options.setPosition(id, k[0])
            else:
                options.setRotation(id, k[0]["s"][0])
                ret = self.__parseK(k)
                options.rotationAnimate(id, ret['arr'], self.__getTime(st))

        if "s" in layer["ks"]:
            k = layer["ks"]["s"]["k"]
            if type(k) ==  types.ListType and  isNum( k[0]) :
                options.setScale(id, k[0] / 100, k[1] / 100)
            else:
                x,y = k[0]["s"][0], k[0]["s"][1]
                options.setScale(id, x / 100, y / 100)
                ret = self.__parseK(k)               
                options.scaleAnimate(id, ret['arr'], self.__getTime(st))


    def __traverseLayer(self, layer,st, id = None):
        ty = layer["ty"]
        options = self.options

        ind = id

        if id:
            ind = id   
        else:    
            if "ind" in layer.keys():
                ind = layer["ind"] 
            else:
                raise Exception("ind not in layer.keys") 

        parentId = self.rootId
        if "parent" in layer.keys():
            parentId = layer["parent"]

        parentInfo = self.getLayer(parentId)
        if "w" not in parentInfo.keys():
            print("here")
        parentWidth = parentInfo["w"]
        parentHeight = parentInfo["h"]

        if ty == Layer.shape:         
            options.createLayer(ind, 0, 0)
            self.__applyTransform(layer, ind, parentId, parentWidth, parentHeight, parentWidth, parentHeight, st)
            options.addChild(ind, parentId)
            for shape in layer["shapes"]:
                self.__traverseShape(shape, ind, parentWidth, parentHeight) 

        elif ty == Layer.solid:
            pass

        elif ty == Layer.image:
            #get the asset info by refId
            refId = layer["refId"]
            asset = self.getAsset(refId)
            if asset == None:
                return
            
            p = asset["p"]
            if not self.useSpriteFrame:
                p = asset["u"] + p
            
            options.createSprite(ind, p, asset['w'], asset['h'])
            options.setContentSize(ind, asset['w'], asset['h'])
            z = 0
            if "z" in layer.keys():
                z = layer["z"]
            options.addChild(ind, parentId, z)
            if 'w' not in layer.keys():
                layer['w'] = asset['w']
                layer['h'] = asset['h']
        
            self.__applyTransform(layer, ind, parentId, asset['w'], asset['h'], parentWidth, parentHeight, st)

        elif ty == Layer.null or ty == Layer.precomp:
            refId = None
            if "refId" in layer:
                refId = layer['refId']
    
            size =  [layer["w"],  layer["h"]] if ty != Layer.null else map(lambda x: x*2,layer["ks"]["a"]["k"])
            width, height =  size[0], size[1]
            if 'w' not in layer.keys():
                layer['w'] = width
                layer['h'] = height

            #effects
            if "ef" in layer.keys():
                for item in layer["ef"]:
                    pass


            asset = None
            if refId:
                asset = self.getAsset(refId)  
           
            if  (asset and  "layers" in asset.keys()):                 
                data = []
                assetLayers = asset["layers"]
                isSequence = True

                for assetLayer in  reversed(assetLayers):
                    if assetLayer['ty'] != Layer.image:
                        raise Exception("ty no supper") 
                    
                    assetLayer_refId = assetLayer["refId"]
                    assetLayer_asset = self.getAsset(assetLayer_refId)
                    if assetLayer_asset == None:
                        raise Exception("no fond assert of assetLayer") 
                    
                    p = assetLayer_asset["p"]
                    if not self.useSpriteFrame:
                        p = assetLayer_asset["u"] + p
                    
                    k = assetLayer["ks"]["p"]["k"]                 
                    _width, _height = 0,0
                    if type(k) ==  types.ListType and  isNum(k[0]):
                        _width, _height =  k[0], parentHeight - k[1]
                    elif type(k) ==  types.ListType and type(k[0]) == types.DictType:                       
                        ret = self.__parseK(k)
                        _width =  ret['arr']
                        isSequence = False
                         
                    k = assetLayer["ks"]["o"]["k"]
                    opacity = k

                    if type(k) == types.ListType and  len(k) > 1:                                               
                        ret = self.__parseK(k)
                        opacity =  ret['arr']
                        isSequence = False

                    k = assetLayer["ks"]["a"]["k"]
                    anchorPointX, anchorPointY = k[0] / width, 1 - k[1] / height

                    k = assetLayer["ks"]["r"]["k"]
                    rotation =  k
                    if type(k) ==  types.ListType:                  
                        ret = self.__parseK(k)
                        rotation =  ret['arr']
                        isSequence = False
                   
                    k = assetLayer["ks"]["s"]["k"]       
                    scaleX, scaleY = 0,0
                    if type(k) ==  types.ListType and not isNum(k[0]):                  
                        ret = self.__parseK(k)
                        scaleX =  ret['arr']
                        isSequence = False
                    else:
                        scaleX, scaleY =  k[0] / 100, k[1] / 100


                    data.append({
                         "path": p,
                          "width": _width,
                          "height":_height ,
                          "opacity":opacity,
                          "anchorPointX":anchorPointX,
                          "anchorPointY": anchorPointY,
                          "rotation":rotation,
                          "parentHeight":parentHeight,
                          "st":self.__getTime(assetLayer['st'])
                     })
                if len(data) > 0 and isSequence:
                    options.animationAnimate(ind, data, isSequence )
                    options.setPosition(ind,data[0]['width'], data[0]['height'])               
                    options.setAnchorPoint(ind,data[0]['anchorPointX'],data[0]['anchorPointY'])
                    options.setOpacity(ind,data[0]['opacity'])
                    options.setRotation(ind,data[0]['rotation'])
                else:   
                    options.createLayer(ind, width, height)               
                    sortedLayers = {}
                    for assetLayer in assetLayers:
                        if "ind" in assetLayer.keys():               
                            self.layers[str(ind) +"_"  +  str(assetLayer ["ind"])] = layer   
                            if "parent" not in assetLayer.keys():
                                if not ind in sortedLayers.keys():
                                    sortedLayers[ind] = []
                                
                                sortedLayers[ind].insert(0, assetLayer)
                                assetLayer["parent"] = ind
                            else:
                                if not str(ind) +"_"  + str(assetLayer["parent"]) in sortedLayers.keys():
                                    sortedLayers[str(ind) +"_"  + str(assetLayer["parent"])] = []                    
                                if assetLayer["parent"] == 0:
                                    sortedLayers[str(ind) +"_"  + str(assetLayer["parent"])].insert(0,assetLayer)
                                else:
                                    sortedLayers[str(ind) +"_"  + str(assetLayer["parent"])].append(assetLayer)
                                assetLayer["parent"] = str(ind) +"_"  + str(assetLayer["parent"])
                            assetLayer["ind"]= str(ind) +"_"  + str(assetLayer["ind"])
                    self.__traverseLayer2(ind, sortedLayers)
            else:
                options.createLayer(ind, width, height)
            self.__applyTransform(layer, ind, parentId, width, height, parentWidth, parentHeight, st)
            options.addChild(ind, parentId)





#lua.ts
class LuaOptions(Options):
    def __init__(self):
        self.mCodeStr = ""
        self.__append( "local t = {}")
        self.__append( "local data = {}")

    def __append(self, code):
        self.mCodeStr += code
        self.mCodeStr += "\n"
    
    def getCode(self):
        return self.mCodeStr + 'return {t = t,data = data}'

    def createLayer(self, id, width, height):   
        self.__append( "t['%s'] = cc.Layer:create()" % id )
        self.__append( "t['%s']:setContentSize(%s, %s)" % (id, str(width), str(height)))
        
    def createSprite(self,id, name, width, height):
        self.__append( "t['%s'] = display.newSprite('%s')" % (id,name) ) 
        #width, height
    
    def setPosition(self,id, x, y):
        self.__append( "t['%s']:setPosition(cc.p(%s, %s))" % (id, str(x), str(y) ))
    
    def positionAnimate(self,id, data, delay, parentHeight):  
        a = []
        t = 0
        for x in data:      
            # temp = "cc.MoveTo:create(%s,cc.p(%s,%s))"%(x["startTime"], x["s"][0], parentHeight - x["s"][1])
            # a.append(temp) 

            if  x["startTime"] - t > 0:
                a.insert(0, "cc.DelayTime:create(%s)"%(x["startTime"] - t)) 
                t = t + x["startTime"]
            t = t + x["t"]

            temp = "cc.BezierTo:create(%s,{cc.p(%s,%s), cc.p(%s,%s), cc.p(%s,%s)} )" %(x["t"], 
                x["s"][0] + x["to"][0] , parentHeight - (x['s'][1] + x['to'][1]),
                x["ti"][0] + x["e"][0] , parentHeight - (x['ti'][1] + x['e'][1]),
                x['e'][0], parentHeight - x['e'][1])
            a.append(temp)        
        
        if delay > 0:
            a.insert(0, "cc.DelayTime:create(%s)"%(delay)) 
    
        self.__append(
            "table.insert(data, {node=t['%s'],action=cc.Sequence:create(%s)})"%(id, ",".join(a))
        ) 

    def setRotation(self,id, rotation):
        self.__append("t['%s']:setRotation(%s)"%(id,rotation));

    def rotationAnimate(self,id, data, delay):
        a = []
        t = 0
        for x in data:      
            # temp = "cc.RotateTo:create(%s, %s)"%(x["startTime"], x["s"][0])
            # a.append(temp) 
            if  x["startTime"] - t > 0:
                a.insert(0, "cc.DelayTime:create(%s)"%(x["startTime"] - t)) 
                t = t + x["startTime"]
            t = t + x["t"]

            temp = "cc.RotateTo:create(%s, %s)"%(x["t"], x["e"][0])            
            a.append(temp)        
        
        if delay > 0:
            a.insert(0, "cc.DelayTime:create(%s)"%(delay)) 
    
        self.__append(
            "table.insert(data, {node=t['%s'],action=cc.Sequence:create(%s)})"%(id, ",".join(a))
        ) 

    def animationAnimate(self,id,data, isSequence):
        if isSequence:
            if len(data) <= 0:
                return 
            self.__append( "t['%s'] = display.newSprite('%s')" % (id,data[0]["path"]) ) 
            
            self.__append( "local animation = cc.Animation:create()")

            for v in data:  
                self.__append( "animation:addSpriteFrameWithFile('%s') " % (v["path"],) )         

            self.__append( "animation:setDelayPerUnit('%s') " % (data[1]["st"] - data[0]["st"],) ) 
            self.__append( "animation:setRestoreOriginalFrame(true)") 
        
            self.__append(
                "table.insert(data, {node=t['%s'],action=cc.Sequence:create(cc.DelayTime:create(%s),cc.Animate:create(animation))})"%(id,data[0]["st"])
            ) 
        # else:
        #     self.__append( "t['%s'] = display.newSprite('%s')" % (id,data[0]["path"]) ) 
        #     for v in data:
        #         temp = []
        #         temp.append("cc.CallFunc:create(function() t['%s']:setTexture('%s') end)", (id,v["path"]) )
                

     

   
    def setScale(self,id, x, y):
        self.__append(
            "t['%s']:setScaleX(%s)"%(id, x)            
        ) 
        
        self.__append(
            "t['%s']:setScaleY(%s)"%(id, y)            
        ) 


    def scaleAnimate(self,id, data, delay):
        a = []
        t = 0
        for x in data:      
            # temp = "cc.ScaleTo:create(%s, %s, %s)"%(x["startTime"], x["s"][0]/100, x["s"][1]/100)
            # a.append(temp) 
            if  x["startTime"] - t > 0:
                a.insert(0, "cc.DelayTime:create(%s)"%(x["startTime"] - t)) 
                t = t + x["startTime"]
            t = t + x["t"]

            temp = "cc.ScaleTo:create(%s, %s, %s)"%(x["t"], x["e"][0]/100, x["e"][1]/100)      
            a.append(temp)        
        
        if delay > 0:
            a.insert(0, "cc.DelayTime:create(%s)"%(delay)) 
    
        self.__append(
            "table.insert(data, {node=t['%s'],action=cc.Sequence:create(%s)})"%(id, ",".join(a))
        )  

    def setContentSize(self,id, width, height):
        self.__append(
            "t['%s']:setContentSize(%s, %s)"%(id, width, height)            
        ) 

    def setAnchorPoint(self,id, x, y):
        self.__append(
            "t['%s']:ignoreAnchorPointForPosition(false)"%(id,)            
        ) 
       
        self.__append(
            "t['%s']:setAnchorPoint(cc.p(%s, %s))"%(id, x, y)            
        ) 

    def moveTo(self,id, parentId, time, x, y):
            pass 


    def addChild(self,id, parentId, localZOrder = None):
        if str(id ) == '<built-in function id>':
            print "run here"
        c = "g"
        if parentId != 'g':
            c =  parentId
        else:
            pass 
        
        self.__append( "t['%s']:addChild(t['%s'])"%(c,id) )
        if localZOrder:
            self.__append( "t['%s']:setLocalZOrder(%s)"%(id, localZOrder) )
         
            
    def getNode(self,id):
        pass 
    
    def setOpacity(self,id, opacity):
        self.__append("t['%s']:setOpacity(%s)"%(id, opacity)) 

    def fadeTo(self,id, data, delay):        
        a = []
        t = 0
        for x in data:
            if  x["startTime"] - t > 0:
                a.insert(0, "cc.DelayTime:create(%s)"%(x["startTime"] - t)) 
                t = t + x["startTime"]
            t = t + x["t"]
            # temp = "cc.FadeTo:create(%s, %s)"%(x["startTime"], x["s"][0]* 2.55)
            # a.append(temp) 

            temp = "cc.FadeTo:create(%s, %s)"%(x["t"], x["e"][0] * 2.55)      
            a.append(temp)        
        
        if delay > 0:
            a.insert(0, "cc.DelayTime:create(%s)"%(delay)) 
    
        self.__append(
            "table.insert(data, {node=t['%s'],action=cc.Sequence:create(%s)})"%(id, ",".join(a))
        )  
    def createDrawNode(self,id, parentId, width):
        if width:
            self.__append( "t['%s'] = cc.DrawNode:create(%s)"% (id, width))
        else:
            self.__append( "t['%s'] = cc.DrawNode:create()"% (id,))
            
        self.__append( "t['%s']:addChild(t['%s'])" % (parentId, id))

    def drawCubicBezier(self,
    id,
    origin,
    c1,
    c2,
    dest,
    width,
    color,
    ):
        points = ",".join(  map(lambda p:"cc.p(%s, %s)"% (p["x"],p["y"]) , [origin, c1, c2, dest]) )
        colorstr = "cc.c4f(%s, %s, %s, %s)"%(color["r"],color["g"],color["b"],color["a"], )
        self.__append("t['%s']:drawCubicBezier(%s ,100, %s)", (points,colorstr ))
    #   append(`t['${id}']:drawCubicBezier(%s, 100, ${convertColor(color)})`)
    # },

f = open('export/data.json')
data = json.load(f)
f.close()
options = LuaOptions()
Traverse(data, 'g', False, options)
print options.getCode()


