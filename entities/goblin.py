"""Goblin: a Being subtype of species 'goblin', used as a test enemy."""

from entities.being import Being


class Goblin(Being):
    def __init__(self, name, **stats):
        super().__init__(name, species="goblin", **stats)
