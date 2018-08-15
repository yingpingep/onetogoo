import json

class Folder:
    def __init__(self, name, oneId="", gooId="", parents=[], children=[]):
        self.name = name
        self.oneId = oneId
        self.gooId = gooId
        self.parents = parents
        self.children = children

    def _Convert(self):
        return {"name": self.name, "oneId": self.oneId, "gooId": self.gooId, "parents": self.parents, "children": self.children}

    def GetPath(self):
        path = "/"
        for p in self.parents:
            path = path + p + "/"
        
        return path    

    def Encoder(obj):
        return json.dumps(obj, cls=FolderEncoder, ensure_ascii=False, indent=4)
    
    def Decoder(jsonStr):
        return json.loads(jsonStr, cls=FolderDecoder)
    
    def ToString(self):
        return "name={0}, oneId={1}, gooId={2}, parents={3}, children={4}".format(self.name, self.oneId, self.gooId, self.parents, self.children)

class FolderEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Folder):
            return obj._Convert()
        elif isinstance(obj, dict):
            temp = {}
            for oKey in obj:
                temp[oKey] = obj[oKey]._Convert()
            return temp

        return super().default(obj)
    
class FolderDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if not "name" in obj:
            temp = {}
            for oKey in obj:
                temp[oKey] = obj[oKey]
            return temp
        else:
            return Folder(obj["name"], obj["oneId"], obj["gooId"], obj["parents"], obj["children"])
