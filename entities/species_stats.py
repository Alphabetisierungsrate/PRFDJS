"""Central registry of default base stats per species.

Keeping these in one place (rather than hardcoded per Being subtype) makes
balancing/tuning and testing straightforward: change a number here and every
Being of that species picks it up, unless a specific instance overrides it.

Species with no entry here fall back to Being's own flat defaults.
"""

SPECIES_BASE_STATS = {
    "human": {
        "max_hp": 20,
        "max_mana": 10,
        "base_attack": 5,
        "base_armor": 5,
        "base_magic": 5,
    },
    "goblin": {
        "max_hp": 12,
        "max_mana": 0,
        "base_attack": 4,
        "base_armor": 2,
        "base_magic": 0,
    },
    "slime": {
        "max_hp": 8,
        "max_mana": 0,
        "base_attack": 2,
        "base_armor": 1,
        "base_magic": 0,
    },
}


def base_stats_for(species):
    """Return a copy of the default stat kwargs for `species` (empty if unregistered)."""
    return dict(SPECIES_BASE_STATS.get(species, {}))
