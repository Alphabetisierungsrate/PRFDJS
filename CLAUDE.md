# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A small, in-progress Python simulation/RPG-style entity system: skills that scale with level via
per-entity random polynomials, living entities ("Beings") with species and skills, and a
contract/quest system with acceptance and status tracking. There is no packaging, dependency
list, build step, or test suite yet — just plain-stdlib Python 3 modules at the repo root.

## Commands

There is no test runner, linter, or build configured. To sanity-check a change, run an ad-hoc
script against the modules directly, e.g.:

```bash
python3 -c "
from human import Human
from skill import Skill
h = Human('Alice')
strength = Skill('strength', degree=2, max_sum=100, max_level=10)
h.acquire_skill(strength)
print(h.skill_value(strength, 5))
"
```

Whenever you change acceptance/status logic in `quest.py` or `quest_board.py`, or the scaling
math in `polynomial.py`/`skill.py`, write one of these throwaway scripts that exercises the
specific edge cases (see recent commit messages for the kinds of scenarios that matter — double
accept, group move-over, leave_group, status transitions, sum-scaling direction) before
considering the change done; there's no automated suite to catch regressions otherwise.

## Architecture

### Skill scaling (`polynomial.py`, `skill.py`)

`generate_random_polynomial(degree, max_sum, coeff_range, num_points)` in `polynomial.py` draws
random coefficients and then **always** rescales them (up or down) so that
`sum(P(x) for x in 1..num_points)` lands exactly on `max_sum` (as long as the raw sum isn't
zero). `num_points` is the parameter that must be passed as the entity's max level for that sum
to be meaningful.

`Skill` (in `skill.py`) is a shared *definition*: it owns the default `degree`, `max_sum`,
`max_level`, and `coeff_range` for that kind of skill — the same `Skill` instance is meant to be
reused across every `Being` that has it. Crucially, `Skill` itself holds no polynomial state.
Each `Being` calls `Skill.acquire_polynomial()` independently (optionally overriding `max_sum`/
`max_level` for that one acquisition, e.g. for a subtype with a different budget or level cap),
so two Beings with the "same" skill always get independently-generated coefficients while
sharing the same default budget/level cap unless overridden.

### Entities (`being.py`, `human.py`, `goblin.py`, `slime.py`)

`Being` is the base for anything living: `name` + `species`, a private `_skills` map (skill →
`{coeffs, max_level}`) built via `acquire_skill`/`skill_value`/`has_skill`, and a `quests` set
that `Quest` keeps in sync (see below) so you can inspect what a Being holds from the Being side
without going through the quest. `Human`, `Goblin`, `Slime` are trivial subtypes that just fix
`species`; Goblin/Slime exist as test enemies.

### Groups (`group.py`)

`Group` is a bare list of member entities with `add_member`/`remove_member`. It exists so
multiple entities can act as a single acceptor on a `Quest` — it has no other behavior.

### Contracts and quests (`contract.py`, `quest.py`, `quest_board.py`)

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

## Git workflow

This repo has no `main`/`master` — the default branch is `claude/random-polynomial-generator-sc3o7o`.
Feature work happens on other branches and is merged directly into that default branch via a
PR that's opened and merged immediately (no long-lived review step currently in use).
