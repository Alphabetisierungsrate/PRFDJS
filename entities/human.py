"""Human: a Being subtype of species 'human'."""

from entities.being import Being


class Human(Being):
    def __init__(self, name, **stats):
        super().__init__(name, species="human", **stats)
