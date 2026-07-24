"""Inventory: a simple bag of items.

A capability an entity *may* have — not every Being carries one (a slime
might drop loot without holding any itself). A Being with an inventory
exposes it as `being.inventory`; one without has `inventory is None`.
"""


class Inventory:
    def __init__(self, items=()):
        self.items = list(items)

    def add(self, item):
        self.items.append(item)

    def remove(self, item):
        self.items.remove(item)

    def __contains__(self, item):
        return item in self.items

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return f"Inventory({self.items!r})"
