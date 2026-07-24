"""SlimeCore: the item a slime drops when slain."""

from items.item import Item


class SlimeCore(Item):
    def __init__(self):
        super().__init__("slime core")
