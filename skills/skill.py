"""Skill definitions describing how a skill scales with level.

A `Skill` carries its own default `max_sum` and `max_level` — the same
skill always comes with the same defaults, no matter which Being possesses
it. It does not hold any polynomial itself: the same `Skill` can be
possessed by many `Being`s, and each one acquires its own individual
polynomial via `Skill.acquire_polynomial()`.

A Being (or a subtype of Being) may override `max_sum` and/or `max_level`
per acquisition, e.g. to give a subtype a different budget or level cap for
an otherwise shared skill.
"""

from skills.polynomial import generate_random_polynomial


class Skill:
    """Defines how a skill of this kind scales with level, by default."""

    def __init__(self, name, degree, max_sum, max_level, coeff_range=(-10.0, 10.0)):
        if max_level < 1:
            raise ValueError("max_level must be >= 1")

        self.name = name
        self.degree = degree
        self.max_sum = max_sum
        self.max_level = max_level
        self.coeff_range = coeff_range

    def acquire_polynomial(self, max_sum=None, max_level=None):
        """Generate a fresh, individual set of scaling coefficients.

        Defaults to this skill's own `max_sum`/`max_level`; either can be
        overridden for a particular acquisition (e.g. a Being subtype with
        a different budget or level cap for this skill).
        """
        if max_sum is None:
            max_sum = self.max_sum
        if max_level is None:
            max_level = self.max_level

        return generate_random_polynomial(
            self.degree, max_sum, coeff_range=self.coeff_range, num_points=max_level
        )

    def value_at(self, coeffs, level, max_level=None):
        """Return the value of a polynomial (as acquired above) at `level`."""
        if max_level is None:
            max_level = self.max_level
        if not 1 <= level <= max_level:
            raise ValueError(f"level must be between 1 and {max_level}")
        return sum(c * level ** k for k, c in enumerate(coeffs))

    def __repr__(self):
        return f"Skill({self.name!r})"
