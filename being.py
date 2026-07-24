"""Being: the base entity for anything living.

Beings (and anything derived from them) can possess skills. Multiple
Beings can possess the same `Skill`, but each Being's polynomial for that
skill is its own — acquired individually, not shared. A skill's `max_sum`
and `max_level` default to whatever the skill itself defines, but a Being
(or a subtype of Being) may override either when acquiring the skill.

A Being's `species` identifies what kind of thing it is (e.g. "human",
"goblin"), separate from its `name` (its individual identity). Stats,
skills, and their max_sum/max_level overrides can later be looked up by
species.

A Being's `quests` is the set of Quests it currently holds (individually
or via a Group it's part of) — kept in sync by Quest.accept/leave_group.
"""


class Being:
    def __init__(self, name, species):
        self.name = name
        self.species = species
        self._skills = {}
        self.quests = set()

    def acquire_skill(self, skill, max_sum=None, max_level=None):
        """Give this Being its own individual polynomial for `skill`.

        `max_sum`/`max_level` default to the skill's own values; pass
        either to override them for this Being (or subtype).

        Calling this again for a skill the Being already has is a no-op;
        it returns the polynomial already acquired rather than regenerating it.
        """
        if skill not in self._skills:
            effective_max_level = skill.max_level if max_level is None else max_level
            coeffs = skill.acquire_polynomial(max_sum=max_sum, max_level=max_level)
            self._skills[skill] = {"coeffs": coeffs, "max_level": effective_max_level}
        return self._skills[skill]["coeffs"]

    def has_skill(self, skill):
        return skill in self._skills

    def skill_value(self, skill, level):
        """Return this Being's scaled value for `skill` at `level`."""
        record = self._skills.get(skill)
        if record is None:
            raise ValueError(f"{self.name} has not acquired skill {skill.name!r}")
        return skill.value_at(record["coeffs"], level, max_level=record["max_level"])
