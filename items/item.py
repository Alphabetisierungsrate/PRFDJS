"""Item: the barebones base for anything that can sit in an inventory or drop."""


class Item:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"{type(self).__name__}(name={self.name!r})"
