"""Skill definitions describing how a skill scales with level.

A `Skill` only holds the parameters that define its scaling (degree,
max_sum, max_level, coeff_range) — it does not hold any polynomial itself.
The same `Skill` can be possessed by many `Being`s, and each one acquires
its own individual polynomial via `Skill.acquire_polynomial()`.
"""

from polynomial import generate_random_polynomial


class Skill:
    """Defines how a skill of this kind scales with level."""

    def __init__(self, name, degree, max_sum, max_level, coeff_range=(-10.0, 10.0)):
        if max_level < 1:
            raise ValueError("max_level must be >= 1")

        self.name = name
        self.degree = degree
        self.max_sum = max_sum
        self.max_level = max_level
        self.coeff_range = coeff_range

    def acquire_polynomial(self):
        """Generate a fresh, individual set of scaling coefficients.

        `max_level` is passed as `num_points` so the sum cap (`max_sum`) is
        computed over this skill's actual level range (1..max_level).
        """
        return generate_random_polynomial(
            self.degree, self.max_sum, coeff_range=self.coeff_range, num_points=self.max_level
        )

    def value_at(self, coeffs, level):
        """Return the value of a polynomial (as acquired above) at `level`."""
        if not 1 <= level <= self.max_level:
            raise ValueError(f"level must be between 1 and {self.max_level}")
        return sum(c * level ** k for k, c in enumerate(coeffs))
