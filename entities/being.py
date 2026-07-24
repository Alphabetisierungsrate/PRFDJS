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

A Being also has stats:
- `hp`/`mana`: `Stat`s (current value bounded by a max). `heal()`/
  `restore_mana()` add to the current value without exceeding the max;
  the max itself can be changed later via `hp.set_max()`/`mana.set_max()`
  (e.g. leveling up, equipment, buffs).
- `base_attack`/`base_armor`/`base_magic`: plain mutable numbers, inputs to
  later damage/defense calculations alongside skills.
- `level`: starts at 1 (never 0, so level-based formulas don't break) and
  `experience`: just a number for now — nothing yet acts on it to level up.

`max_hp`/`max_mana`/`base_attack`/`base_armor`/`base_magic` default to this
Being's species entry in `species_stats.SPECIES_BASE_STATS` (falling back to
a flat 10/10/0/0/0 for an unregistered species) so base values for balancing
live in one central place instead of being hardcoded per subtype. Passing
any of them explicitly overrides the species default for that one Being.

An inventory is an optional capability, not something every Being carries:
pass `has_inventory=True` to give this Being an `Inventory` (otherwise
`inventory is None`). `drops` is the list of items this Being yields when
slain; another Being with an inventory can `loot()` them.
"""

from entities.inventory import Inventory
from entities.species_stats import base_stats_for
from entities.stat import Stat


class Being:
    def __init__(
        self,
        name,
        species,
        max_hp=None,
        max_mana=None,
        base_attack=None,
        base_armor=None,
        base_magic=None,
        level=1,
        experience=0,
        has_inventory=False,
        drops=None,
    ):
        if level < 1:
            raise ValueError("level must be >= 1")

        defaults = base_stats_for(species)

        self.name = name
        self.species = species
        self._skills = {}
        self.quests = set()

        self.hp = Stat(max_hp if max_hp is not None else defaults.get("max_hp", 10))
        self.mana = Stat(max_mana if max_mana is not None else defaults.get("max_mana", 10))
        self.base_attack = base_attack if base_attack is not None else defaults.get("base_attack", 0)
        self.base_armor = base_armor if base_armor is not None else defaults.get("base_armor", 0)
        self.base_magic = base_magic if base_magic is not None else defaults.get("base_magic", 0)
        self.level = level
        self.experience = experience

        self.inventory = Inventory() if has_inventory else None
        self.drops = list(drops) if drops else []

    def __repr__(self):
        return (
            f"{type(self).__name__}(name={self.name!r}, species={self.species!r}, "
            f"level={self.level})"
        )

    def heal(self, amount):
        """Add `amount` to current HP, capped at max HP (and not below 0)."""
        self.hp.add(amount)

    def restore_mana(self, amount):
        """Add `amount` to current mana, capped at max mana (and not below 0)."""
        self.mana.add(amount)

    def pick_up(self, item):
        """Put `item` into this Being's inventory (raises if it has none)."""
        if self.inventory is None:
            raise ValueError(f"{self.name} has no inventory to hold {item!r}")
        self.inventory.add(item)
        return item

    def loot(self, other):
        """Move all of `other`'s drops into this Being's inventory.

        Raises if this Being has no inventory. Returns the looted items and
        empties `other.drops` so the same drops can't be looted twice.
        """
        if self.inventory is None:
            raise ValueError(f"{self.name} has no inventory to loot into")
        looted = list(other.drops)
        for item in looted:
            self.inventory.add(item)
        other.drops = []
        return looted

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
