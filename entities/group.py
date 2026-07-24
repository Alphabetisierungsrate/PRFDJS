"""Group: a set of entities that can act together, e.g. to accept a quest jointly."""


class Group:
    def __init__(self, members=()):
        self.members = list(members)

    def add_member(self, entity):
        if entity not in self.members:
            self.members.append(entity)

    def remove_member(self, entity):
        if entity in self.members:
            self.members.remove(entity)

    def __repr__(self):
        return f"Group({self.members!r})"
