"""QuestBoard: a place quests can be posted to for visibility, and accepted from.

Posting a quest to a board just makes it visible there — it is not the
only way a quest can be given out or accepted; quests can still change
hands directly via Quest.accept() without ever touching a board.
"""


class QuestBoard:
    def __init__(self, name):
        self.name = name
        self.posted_quests = []

    def post(self, quest):
        if quest not in self.posted_quests:
            self.posted_quests.append(quest)

    def unpost(self, quest):
        if quest in self.posted_quests:
            self.posted_quests.remove(quest)

    @property
    def open_quests(self):
        """Posted quests that still have room for another acceptor."""
        return [quest for quest in self.posted_quests if quest.is_open]

    def accept(self, quest, acceptor):
        """Accept a quest posted on this board, on behalf of `acceptor`."""
        if quest not in self.posted_quests:
            raise ValueError(f"{quest!r} is not posted on this board")
        quest.accept(acceptor)
