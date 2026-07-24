"""Contract: a barebones base for binding agreements or effects.

A Contract has conditions that must all be met for it to be successful.
Subtypes share this (Quest today; curses or other effects later).
"""


class Contract:
    def __init__(self, name, conditions=()):
        """`conditions` is an iterable of zero-arg callables returning bool."""
        self.name = name
        self.conditions = list(conditions)

    def is_successful(self):
        """A Contract is successful once every one of its conditions is met."""
        return all(condition() for condition in self.conditions)
