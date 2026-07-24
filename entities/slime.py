"""Slime: a Being subtype of species 'slime', used as a test enemy."""

from entities.being import Being


class Slime(Being):
    def __init__(self, name, **stats):
        super().__init__(name, species="slime", **stats)
