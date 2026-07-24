"""Skills that scale with level according to a per-skill polynomial."""

from polynomial import generate_random_polynomial


class Skill:
    """A skill whose value at each level is given by a fixed polynomial.

    The polynomial is acquired once, at construction time, via
    `generate_random_polynomial`. The skill's `max_level` is passed as
    `num_points` so the sum cap (`max_sum`) is computed over the skill's
    actual level range (1..max_level) rather than the generator's default,
    which keeps the resulting sum accurate for this use case.
    """

    def __init__(self, name, degree, max_sum, max_level, coeff_range=(-10.0, 10.0)):
        if max_level < 1:
            raise ValueError("max_level must be >= 1")

        self.name = name
        self.max_level = max_level
        self.coeffs = generate_random_polynomial(
            degree, max_sum, coeff_range=coeff_range, num_points=max_level
        )

    def value_at(self, level):
        """Return the skill's scaled value at `level` (1..max_level)."""
        if not 1 <= level <= self.max_level:
            raise ValueError(f"level must be between 1 and {self.max_level}")
        return sum(c * level ** k for k, c in enumerate(self.coeffs))
