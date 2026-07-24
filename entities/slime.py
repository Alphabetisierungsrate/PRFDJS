"""Slime: a Being subtype of species 'slime', used as a test enemy."""

from entities.being import Being


class Slime(Being):
    def __init__(self, name):
        super().__init__(name, species="slime")
