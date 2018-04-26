
#-*-coding:utf-8-*-
from __future__ import division
import json
import types

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


def convertColor(c):
    return map(lambda n: n * 0xFF, c)

def isNum(d):
    return type(d) == types.FloatType or type(d) == types.IntType or type(d) == types.LongType
       
class Traverse:
    def __init__(self, data, useSpriteFrame):
        self.assets = {} #记录所有的assets信息
        self.layers = {} #记录所有的layer信息
        self.data = data

        self.mRet = {} #将要输出的数据
        self.mRet["w"] =  data["w"]
        self.mRet["h"] =  data["h"]

        #根节点尺寸
        self.rootWidth =  data["w"]
        self.rootHeight = data["h"]

        self.useSpriteFrame = useSpriteFrame

        #初使化asset
        for asset in data['assets']:
            if "id" in asset.keys():               
                self.assets[asset["id"]] = asset

        #初使化layer
        sortedLayers = []
     
        for layer in data["layers"]:
            if "ind" in layer.keys():               
                self.layers[layer["ind"]] = layer
                if "parent" not in layer.keys():
                    sortedLayers.insert(0, layer)
                elif layer["parent"] == 0:
                    sortedLayers.insert(0, layer)
                else:
                    sortedLayers.append(layer)
        
        #解析层
        self.mRet["layers"] = []
        for layer in sortedLayers:
            self.mRet["layers"].append( self.__traverseLayer(layer) )

    def getRet(self):
        return self.mRet

    def __getTime(self, time):
        return time / self.data['fr']

    def __getAsset(self, refId):
        if refId in self.assets.keys():
            return self.assets[refId]
        return None
    
    def __getLayer(self, ind):
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
        return ret["arr"]

    def __applyTransform(self, layer,  width,  height,  parentWidth,  parentHeight,  ret):
        #显示时间
        if "ip" in layer.keys():
            ret["st"] = self.__getTime(layer["ip"])
        #隐藏时间
        if "op" in layer.keys():
            ret["et"] = self.__getTime(layer["op"])
        
        #帧的变化
        if not "ks" in layer.keys():
            return 
        
        if "o" in layer["ks"]:
            k = layer["ks"]["o"]["k"]
            if type(k) == types.ListType and  len(k) > 1:
                opacity = k[0]["s"][0]
                ret["o"] =  opacity * 2.55

                retK = self.__parseK(k)
                ret["oa"] = []
                for d in retK:
                    ret["oa"].append( {
                        "st" : d["startTime"],
                        "t" : d['t'],
                        's' : d["s"][0] * 2.55,
                        'e' : d['e'][0] * 2.55
                    })
            elif isNum(k):
                ret["o"] =  k * 2.55
              

        if "a" in layer["ks"]:
            k = layer["ks"]["a"]["k"]
            if type(k) == types.DictType and  "x" in k.keys():
                ret["ax"] =  k['x'] / width
                ret["ay"] = 1 - k['y'] / height                       
            else:
                if width != 0 and  height != 0:
                    ret["ax"] = k[0] / width
                    ret["ay"] = 1 - k[1] / height    
                 

        if "p" in layer["ks"]:
            k = layer["ks"]["p"]["k"]
            if type(k) ==  types.ListType and  isNum(k[0]):
                ret["x"] =  k[0]
                ret["y"] = parentHeight - k[1]           
            elif type(k) ==  types.ListType and type(k[0]) == types.DictType:
                x, y = k[0]['s'][0],k[0]['s'][1]
                ret["x"] =   x
                ret["y"] = parentHeight - y

                retK = self.__parseK(k)
                ret["pa"] = []
                for d in retK:
                    ret["pa"].append( {
                        "st" : d["startTime"],
                        "t" : d['t'],
                        "s":[d["s"][0], parentHeight - d["s"][1]],
                        "e":[d["e"][0], parentHeight - d["e"][1]],
                        'p1' : [d["s"][0] + d["to"][0] , parentHeight - (d['s'][1] + d['to'][1])],
                        'p2' : [d["ti"][0] + d["e"][0] , parentHeight - (d['ti'][1] + d['e'][1])],
                        'p3' : [d['e'][0], parentHeight - d['e'][1]]
                    })

        if "r" in layer["ks"]:
            k = layer["ks"]["r"]["k"]
            if isNum(k):
                ret["r"] = k
               
            elif type(k) ==  types.ListType and isNum( k[0])  :                              
                ret["r"] = k[0]
            else:
                ret["r"] =k[0]["s"][0]               
                retK = self.__parseK(k)
                ret["ra"] = []
                for d in retK:
                    ret["ra"].append( {
                        "st" : d["startTime"],
                        "t" : d['t'],
                        's' : d["s"][0],
                        'e' : d['e'][0]
                    })
             
        if "s" in layer["ks"]:
            k = layer["ks"]["s"]["k"]
            if type(k) ==  types.ListType and  isNum( k[0]) :
                ret["sx"] = k[0] / 100
                ret['sy'] = k[1] / 100           
            else:
                x,y = k[0]["s"][0], k[0]["s"][1]
                ret["sx"] = x/ 100
                ret['sy'] = y/ 100
              
                retK = self.__parseK(k)               
                ret["sa"] = []
                for d in retK:
                    ret["sa"].append( {
                        "st" : d["startTime"],
                        "t" : d['t'],
                        's' : [d["s"][0]/100,d["s"][1]/100],
                        'e' : [d['e'][0]/100,d["e"][1]/100],
                    })


    def __traverseLayer(self, layer):
        ret = {}

        #层的类型
        ty = layer["ty"]
      
        #获取层id
        ind = None
        if "ind" in layer.keys():
            ind = layer["ind"] 
        else:
            raise Exception("ind not in layer.keys") 
        ret["id"] =  ind 

        #获取层的parent
        parentId = None
        if "parent" in layer.keys():
            parentId = layer["parent"]
            ret["parent"] = parentId
       

        #获取父节点的长宽
        parentWidth, parentHeight = self.rootWidth,self.rootHeight
        parentInfo = self.__getLayer(parentId)
        if parentInfo:
            if "w" not in parentInfo.keys():
                #为了获取父节点的宽高
                self.__traverseLayer(parentInfo)
          
            parentWidth, parentHeight = parentInfo['w'],parentInfo['h']
        
        if ty == Layer.shape:  
            pass       
            # options.createLayer(ind, 0, 0)
            # self.__applyTransform(layer, ind, parentId, parentWidth, parentHeight, parentWidth, parentHeight, st)
            # options.addChild(ind, parentId)
            # for shape in layer["shapes"]:
            #     self.__traverseShape(shape, ind, parentWidth, parentHeight) 

        elif ty == Layer.solid:
            pass

        elif ty == Layer.image:
            #获取图层信息
            refId = layer["refId"]
            asset = self.__getAsset(refId)
            if asset == None:
                return
            
            #获取图层的图片路径
            p = asset["p"]
            if not self.useSpriteFrame:
                p = asset["u"] + p

            ret["texture"] = p
            layer["w"], layer['h'] = asset['w'], asset['h']
            self.__applyTransform(layer, asset['w'], asset['h'], parentWidth, parentHeight, ret)

        elif ty == Layer.null or ty == Layer.precomp:
            refId = None
            if "refId" in layer:
                refId = layer['refId']

            #获取层的尺寸
            size =  [layer["w"],  layer["h"]] if ty != Layer.null else map(lambda x: x*2,layer["ks"]["a"]["k"])
            width, height =  size[0], size[1]
            if 'w' not in layer.keys():
                layer['w'] = width
                layer['h'] = height
            ret["w"] = width
            ret["h"] = height

            #effects(不支持)
            if "ef" in layer.keys():
                for item in layer["ef"]:
                    pass

            self.__applyTransform(layer, width, height, parentWidth, parentHeight, ret)        
            
            #是否是组合层
            asset = None
            if refId:
                asset = self.__getAsset(refId)  

            if  (asset and  "layers" in asset.keys()):
                ret["module"] = {}
                
                asset['w'] = layer['w']
                asset['h'] = layer['h']
                asset['assets'] = self.data['assets']
                asset["fr"] = self.data['fr']

                traverse = Traverse(asset,  self.useSpriteFrame)
                ret["module"] = traverse.getRet()
        return  ret





f = open('export/data.json')
data = json.load(f)
f.close()
t = Traverse(data, False)

print json.dumps(t.getRet())


