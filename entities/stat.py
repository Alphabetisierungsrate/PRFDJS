"""Stat: a bounded resource with a current value and a max, e.g. HP or mana."""


class Stat:
    def __init__(self, max_value):
        if max_value < 0:
            raise ValueError("max_value must be >= 0")
        self.max_value = max_value
        self.current = max_value

    def add(self, amount):
        """Add `amount` to `current`, clamped to [0, max_value].

        A positive amount heals/restores; a negative amount depletes it.
        """
        self.current = max(0, min(self.max_value, self.current + amount))

    def set_max(self, new_max):
        """Change `max_value`; `current` is clamped down if it now exceeds it."""
        if new_max < 0:
            raise ValueError("new_max must be >= 0")
        self.max_value = new_max
        self.current = min(self.current, self.max_value)

    def __repr__(self):
        return f"Stat(current={self.current}, max={self.max_value})"
