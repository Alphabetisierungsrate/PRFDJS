"""Goblin: a Being subtype of species 'goblin', used as a test enemy."""

from entities.being import Being


class Goblin(Being):
    def __init__(self, name):
        super().__init__(name, species="goblin")
