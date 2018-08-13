from json import JSONEncoder

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

class FolderConvert(JSONEncoder):
    def default(self, o):
        if isinstance(o, Folder):
            return o._Convert()
        elif isinstance(o, dict):
            temp = {}
            for oKey in o:
                temp[oKey] = o[oKey]._Convert()
            return temp

        return super().default(o)