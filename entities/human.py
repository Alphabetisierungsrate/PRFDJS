"""Human: a Being subtype of species 'human'."""

from entities.being import Being


class Human(Being):
    def __init__(self, name):
        super().__init__(name, species="human")
