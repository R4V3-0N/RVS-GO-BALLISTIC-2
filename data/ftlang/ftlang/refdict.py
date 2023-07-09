
class ProtoDict:
    def __init__(self, parent=None):
        self.dict = {}
        self.parent = parent

    def copy(self):
        return ProtoDict(self)

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __contains__(self, key):
        return key in self.dict or (self.parent is not None and key in self.parent)

    def __getitem__(self, key):
        if key in self.dict:
            return self.dict[key]
        elif self.parent is not None:
            return self.parent
        else:
            raise KeyError(key)
