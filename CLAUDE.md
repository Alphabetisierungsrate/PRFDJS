# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A small, in-progress Python simulation/RPG-style entity system: skills that scale with level via
per-entity random polynomials, living entities ("Beings") with species and skills, and a
contract/quest system with acceptance and status tracking. There is no packaging, dependency
list, or build step — just plain-stdlib Python 3 packages at the repo root:

- `entities/` — `Being` and its subtypes, `Group`, `Stat`, `Inventory`, species base stats
- `skills/` — the polynomial scaling math and the `Skill` definition
- `quests/` — `Contract`, `Quest`, `QuestBoard`
- `encounters/` — `Encounter`, `Action`, `Attack` (tick-driven combat)
- `items/` — `Item` and its subtypes (e.g. `SlimeCore`)
- `world/` — `Clock`, the global tick counter shared across systems
- `maps/` — `Hex` and `HexMap` (hex-grid maps, one instance per map)
- `tests/` — mirrors the packages above; `tests/test_scenario.py` is a cross-package
  integration scenario

## Commands

There is no build or lint configured. Tests use the standard library's `unittest` (no
dependencies to install):

```bash
python3 -m unittest discover -v
```

To run a single test file or a single test:

```bash
python3 -m unittest tests.quests.test_quest -v
python3 -m unittest tests.quests.test_quest.QuestAcceptanceTests.test_leave_group_loses_quest_when_no_slot_free -v
```

When you change acceptance/status logic in `quests/quest.py`/`quests/quest_board.py`, the scaling
math in `skills/polynomial.py`/`skills/skill.py`, or the tick/timing logic in
`encounters/encounter.py`, add a case to the matching `tests/**/test_*.py` file rather than
verifying with a one-off script — the suite is the source of truth for the edge cases that matter
(double accept, group move-over, leave_group, status transitions, sum-scaling direction, zero-sum
polynomial draws, exact-tick action resolution).

## Architecture

### Skill scaling (`skills/polynomial.py`, `skills/skill.py`)

`generate_random_polynomial(degree, max_sum, coeff_range, num_points)` in `skills/polynomial.py` draws
random coefficients and then **always** rescales them (up or down) so that
`sum(P(x) for x in 1..num_points)` lands exactly on `max_sum`. On the rare draw whose raw sum is
exactly zero (unscalable), it redraws rather than returning coefficients that don't hit
`max_sum`. `num_points` is the parameter that must be passed as the entity's max level for that
sum to be meaningful.

`Skill` (in `skills/skill.py`) is a shared *definition*: it owns the default `degree`, `max_sum`,
`max_level`, and `coeff_range` for that kind of skill — the same `Skill` instance is meant to be
reused across every `Being` that has it. Crucially, `Skill` itself holds no polynomial state.
Each `Being` calls `Skill.acquire_polynomial()` independently (optionally overriding `max_sum`/
`max_level` for that one acquisition, e.g. for a subtype with a different budget or level cap),
so two Beings with the "same" skill always get independently-generated coefficients while
sharing the same default budget/level cap unless overridden.

### Entities (`entities/being.py`, `entities/stat.py`, `entities/species_stats.py`, `entities/human.py`, `entities/goblin.py`, `entities/slime.py`)

`Being` is the base for anything living: `name` + `species`, a private `_skills` map (skill →
`{coeffs, max_level}`) built via `acquire_skill`/`skill_value`/`has_skill`, and a `quests` set
that `Quest` keeps in sync (see below) so you can inspect what a Being holds from the Being side
without going through the quest. `Human`, `Goblin`, `Slime` are trivial subtypes that just fix
`species` and forward any stat overrides (`**stats`) to `Being`; Goblin/Slime exist as test
enemies.

A Being's stats:
- `hp`/`mana` are `Stat`s (`entities/stat.py`): a `current` value bounded by `max_value`.
  `Being.heal()`/`restore_mana()` add to `current` without exceeding `max_value` (or going below
  0); `Stat.set_max()` changes `max_value` itself (leveling up, equipment, etc.), clamping
  `current` down if it now exceeds the new max. A Being starts at full HP/mana.
- `base_attack`/`base_armor`/`base_magic` are plain mutable numbers, meant as inputs to future
  damage/defense calculations alongside skills — no current/max split, just set them directly.
- `level` starts at 1 and is validated `>= 1` (so level-based formulas, like skill scaling, never
  see a 0 or negative level). `experience` is just a stored number for now; nothing acts on it to
  level up yet.

`max_hp`/`max_mana`/`base_attack`/`base_armor`/`base_magic` default to whatever
`species_stats.SPECIES_BASE_STATS` has registered for that Being's species (falling back to a
flat 10/10/0/0/0 for an unregistered species), rather than being hardcoded per subtype — this is
the central place to tune enemy/ally base values for balancing. Passing any of them explicitly at
construction (directly or via a subtype's `**stats`) overrides the species default for that one
Being only.

An **inventory is optional**, not something every Being has: `has_inventory=True` gives a Being an
`Inventory` (`entities/inventory.py`, a simple item bag), otherwise `being.inventory is None`.
`drops` is the list of items a Being yields when slain; `Being.loot(other)` moves another Being's
`drops` into this one's inventory (and empties them), and `Being.pick_up(item)` adds a single
item — both raise if this Being has no inventory. Items live in `items/` (`Item` base, subtypes
like `SlimeCore`).

### Groups (`entities/group.py`)

`Group` is a bare list of member entities with `add_member`/`remove_member`. It exists so
multiple entities can act as a single acceptor on a `Quest` — it has no other behavior.

### Contracts and quests (`quests/contract.py`, `quests/quest.py`, `quests/quest_board.py`)

`Contract` is the deliberately barebones base for any binding agreement/effect: a `name` and a
list of zero-arg `conditions` callables, with `is_successful()` = all conditions true. This lives
on `Contract`, not `Quest`, because future subtypes (e.g. curses) need it too.

`Quest(Contract)` adds:
- a `provider` (whatever opened the quest — a Being, an institution, anything)
- acceptance: `accept(acceptor)` where `acceptor` is either an individual entity or a `Group`.
  Whether the quest allows more than one concurrent acceptor, and the max if so, is fixed at
  construction (`allow_multiple` / `max_acceptors`).
- anti-double-dip bookkeeping via `_entity_coverage` (entity → whatever currently covers it —
  itself, or a Group): an entity can't accept twice, and can't hold a quest both individually and
  via a group simultaneously. The one asymmetry: if a Group accepts and one of its members
  already held the quest individually, that individual acceptance is *moved over* into the
  group's rather than rejected. The reverse (accepting individually while already covered by a
  group) is a hard rejection. `leave_group(group, entity)` hands the quest back to the entity
  individually if the quest allows multiple acceptors and a slot is free — regardless of whether
  that entity ever held it individually before the group picked it up.
- `status`, a `QuestStatus` enum: `OPEN`/`TAKEN` are derived automatically from whether the quest
  has a free acceptor slot (kept in sync by a `_sync_open_taken_status()` call at the end of
  `accept()`/`leave_group()`); `COMPLETED`/`FAILED`/`EXPIRED` are terminal and only set explicitly
  via `complete()`/`fail()`/`expire()` — once resolved, a quest rejects further `accept()` calls
  and further resolution calls. `expire()` specifically means "closed without ever being
  accepted" and raises if the quest already has an acceptor (use `fail()` for that case instead).

`QuestBoard` is just a posting/visibility layer on top of `Quest` — `post`/`unpost`, and
`open_quests`/`taken_quests` properties for displaying those two states differently, plus
`remove_resolved()` to prune completed/failed/expired quests. Posting to a board is optional and
not the only way a quest can be given out or accepted; `Quest.accept()` works standalone.

### The global clock (`world/clock.py`)

`Clock` is the single, shared measure of in-game time — **time is not owned by any encounter or
system**. `advance()` moves it forward by exactly one tick and never jumps ahead to "the next
interesting moment". Everything that cares about timing reads one clock's `current_tick` and
schedules against it, so several fights (and, later, multiplayer) can run against the same tick
line without callers having to coordinate.

### Encounters (`encounters/action.py`, `encounters/attack.py`, `encounters/encounter.py`)

`Encounter(a, b, clock)` is a tick-driven fight — for now strictly 1 vs 1, no location/environment
concept. It **does not own time**: it reads the shared `Clock` passed in (`encounter.current_tick`
just proxies `clock.current_tick`). To drive a fight you advance the clock yourself and then call
`encounter.resolve_due()`, which applies any actions that have come due at the current tick and
returns them (see `tests/test_scenario.py`'s `run_encounter` helper for the canonical loop). This
separation is deliberate: either entity can have an action started for it the instant it's free,
independent of what the other is doing (including mid-wind-up of its own action); the `log` comes
out in strict tick order by construction; and because the clock is global rather than
per-encounter, concurrent fights and eventual multiplayer stay tractable.

`Action` (in `action.py`) bundles an `actor`, a `target`, and a `duration` in ticks; `apply()` is
its effect, called by `resolve_due()` once `duration` ticks have elapsed since
`Encounter.start_action()` queued it. `Attack` (in `attack.py`) is the only action so far: fixed
`duration`, deals `attacker.base_attack - defender.base_armor` (floored at 0) to the target's `hp`.

An entity can only have one action in flight at a time (`is_ready()`/`start_action()` enforce
this), but the two entities' actions are otherwise independent — `Encounter` doesn't wait for one
to resolve before letting the other start. An action already in flight resolves at its scheduled
tick even if its actor has since died in the same resolution pass (`resolve_due()` processes `a`
then `b`) — ticks don't rewind the past, so two attacks due on the same tick both land, allowing a
genuine mutual-kill/draw.

### Maps (`maps/hex.py`, `maps/hex_map.py`)

Maps are hex grids, and each map is its own `HexMap` instance — there is no single global grid.
`Hex` is an immutable, hashable axial coordinate `(q, r)` (with cube `s = -q - r` derived on
demand); its six `neighbors()` and `distance()` are pure coordinate math. **The coordinate layer
is orientation-agnostic** — pointy-top vs flat-top only changes rendering, not the math, so
nothing commits to one yet (pointy-top is the plan for when rendering is added).

A `HexMap` is any set of `Hex`es with one enforced invariant, checked by BFS flood-fill at
construction: every hex must be reachable from every other through adjacent in-map hexes. That
permits arbitrary shapes (solid blobs, rings with a hole in the middle, lines) but rejects
disconnected islands. `HexMap.neighbors(cell)` returns only in-map neighbors; `shortest_path()`/
`distance()` are BFS over in-map hexes and therefore route *around* holes (distinct from
`Hex.distance`, which is straight-line and ignores shape). `HexMap.hexagon(radius)` builds a solid
hexagonal map. Nothing places entities on maps yet — movement/positioning is future work.

## Conventions

`Being`, `Group`, `Skill`, `Contract`, and `Quest` all define `__repr__` (name/species, quest
status, etc.) so error messages and debugging output are readable instead of showing raw object
addresses — add one to any new core class in the same style.

## Git workflow

This repo has no `main`/`master` — the default branch is `claude/random-polynomial-generator-sc3o7o`.
Feature work happens on other branches and is merged directly into that default branch via a
PR that's opened and merged immediately (no long-lived review step currently in use).
