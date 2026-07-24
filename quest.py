"""Quest: a Contract that succeeds once all of its conditions are met."""

from contract import Contract


class Quest(Contract):
    def __init__(self, name, conditions):
        """`conditions` is an iterable of zero-arg callables returning bool."""
        super().__init__(name)
        self.conditions = list(conditions)

    def is_successful(self):
        """A Quest is successful once every one of its conditions is met."""
        return all(condition() for condition in self.conditions)
