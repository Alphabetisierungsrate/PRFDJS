"""Being: the base entity for anything living.

Beings (and anything derived from them) can possess skills. Multiple
Beings can possess the same `Skill`, but each Being's polynomial for that
skill is its own — acquired individually, not shared.
"""


class Being:
    def __init__(self, name):
        self.name = name
        self._skill_polynomials = {}

    def acquire_skill(self, skill):
        """Give this Being its own individual polynomial for `skill`.

        Calling this again for a skill the Being already has is a no-op;
        it returns the polynomial already acquired rather than regenerating it.
        """
        if skill not in self._skill_polynomials:
            self._skill_polynomials[skill] = skill.acquire_polynomial()
        return self._skill_polynomials[skill]

    def has_skill(self, skill):
        return skill in self._skill_polynomials

    def skill_value(self, skill, level):
        """Return this Being's scaled value for `skill` at `level`."""
        coeffs = self._skill_polynomials.get(skill)
        if coeffs is None:
            raise ValueError(f"{self.name} has not acquired skill {skill.name!r}")
        return skill.value_at(coeffs, level)
