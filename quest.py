"""Quest: a Contract provided by one entity and accepted by others.

A quest is opened by a `provider` (a Being, an institution, etc. — anything
can provide a quest). It starts unaccepted; a quest can sit open with no
acceptor at all. It's accepted by either a single entity or a `Group` of
entities acting together; whether more than one entity/group can hold it
concurrently — and if so, the maximum number of acceptors — is fixed when
the quest is created.

An entity can never double dip: it can't accept the same quest twice, and
it can't hold the quest both individually and via a group at the same
time. If a Group accepts the quest and one of its members already held it
individually, that member's individual acceptance is folded into the
group's (moved over, not rejected). The reverse — accepting individually
while already covered via a group — is rejected outright. If a member
leaves a group that holds the quest, they retain it individually as long
as the quest allows multiple acceptors and a slot is free — this applies
regardless of whether they'd held it individually before the group ever
picked it up. Otherwise they simply lose it.

Every entity that ends up holding a quest (individually or via a group)
gets it added to its own `quests` set, kept in sync as coverage changes.

Every quest also carries a `status`:
- OPEN: still has room for another acceptor.
- TAKEN: fully accepted, no room left.
- COMPLETED: resolved as a success.
- FAILED: resolved as a failure (e.g. accepted but not pulled off).
- EXPIRED: closed/timed out without ever being accepted at all.
COMPLETED, FAILED, and EXPIRED are terminal: a quest can't move on from
them, and it can no longer be accepted once resolved. OPEN/TAKEN are kept
in sync automatically as acceptors come and go; the terminal states are
only ever set explicitly, via complete()/fail()/expire().
"""

from enum import Enum

from contract import Contract
from group import Group


class QuestStatus(Enum):
    OPEN = "open"
    TAKEN = "taken"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class Quest(Contract):
    def __init__(self, name, provider, conditions=(), allow_multiple=False, max_acceptors=None):
        super().__init__(name, conditions)
        self.provider = provider
        self.allow_multiple = allow_multiple

        if allow_multiple:
            if max_acceptors is None or max_acceptors < 1:
                raise ValueError("max_acceptors must be a positive integer when allow_multiple is True")
            self.max_acceptors = max_acceptors
        else:
            self.max_acceptors = 1

        self._acceptors = []
        self._entity_coverage = {}
        self.status = QuestStatus.OPEN

    def __repr__(self):
        return f"Quest({self.name!r}, status={self.status.value})"

    @property
    def is_open(self):
        """Whether the quest still has room for another acceptor."""
        return len(self._acceptors) < self.max_acceptors

    @property
    def is_resolved(self):
        """Whether the quest has reached a terminal status."""
        return self.status in (QuestStatus.COMPLETED, QuestStatus.FAILED, QuestStatus.EXPIRED)

    def _sync_open_taken_status(self):
        if not self.is_resolved:
            self.status = QuestStatus.OPEN if self.is_open else QuestStatus.TAKEN

    def complete(self):
        """Mark the quest resolved as a success."""
        self._resolve_as(QuestStatus.COMPLETED)

    def fail(self):
        """Mark the quest resolved as a failure."""
        self._resolve_as(QuestStatus.FAILED)

    def expire(self):
        """Mark the quest resolved as expired: it closed/timed out unaccepted."""
        if self._acceptors:
            raise ValueError("only a quest with no acceptors can expire")
        self._resolve_as(QuestStatus.EXPIRED)

    def _resolve_as(self, status):
        if self.is_resolved:
            raise ValueError(f"quest is already {self.status.value}")
        self.status = status

    def accepted_by(self, entity):
        """The acceptor (the entity itself, or the Group) covering `entity`, or None."""
        return self._entity_coverage.get(entity)

    def accept(self, acceptor):
        """Accept the quest on behalf of `acceptor` (an entity or a Group)."""
        if self.is_resolved:
            raise ValueError(f"quest is {self.status.value} and can no longer be accepted")

        members = list(acceptor.members) if isinstance(acceptor, Group) else [acceptor]

        moving_over = []
        for member in members:
            coverage = self._entity_coverage.get(member)
            if coverage is None:
                continue
            if coverage is member:
                if isinstance(acceptor, Group):
                    moving_over.append(member)
                    continue
                raise ValueError(f"{member!r} has already accepted this quest")
            if coverage is acceptor:
                raise ValueError(f"{acceptor!r} has already accepted this quest")
            raise ValueError(f"{member!r} already holds this quest via {coverage!r}")

        remaining_slots = self.max_acceptors - (len(self._acceptors) - len(moving_over))
        if remaining_slots < 1:
            raise ValueError("this quest has no room for another acceptor")

        for member in moving_over:
            self._acceptors.remove(member)

        self._acceptors.append(acceptor)
        for member in members:
            self._entity_coverage[member] = acceptor
            member.quests.add(self)
        self._sync_open_taken_status()

    def leave_group(self, group, entity):
        """`entity` leaves `group`, which holds this quest.

        `entity` retains the quest individually if it allows multiple
        acceptors and a slot is free — whether or not `entity` held the
        quest individually before the group ever accepted it. Otherwise it
        simply loses the quest.
        """
        if self._entity_coverage.get(entity) is not group:
            raise ValueError(f"{entity!r} does not hold this quest via {group!r}")

        group.remove_member(entity)
        del self._entity_coverage[entity]

        if not group.members:
            self._acceptors.remove(group)

        if self.allow_multiple and len(self._acceptors) < self.max_acceptors:
            self._acceptors.append(entity)
            self._entity_coverage[entity] = entity
        else:
            entity.quests.discard(self)

        self._sync_open_taken_status()
