"""Contract: a barebones base for binding agreements or effects.

Deliberately minimal for now — later subtypes may include things like
curses, in addition to Quest.
"""


class Contract:
    def __init__(self, name):
        self.name = name
