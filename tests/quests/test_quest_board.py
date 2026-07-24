import unittest

from entities.human import Human
from quests.quest import Quest
from quests.quest_board import QuestBoard


class QuestBoardTests(unittest.TestCase):
    def setUp(self):
        self.provider = Human("Elder")
        self.alice = Human("Alice")
        self.board = QuestBoard("Town Square")

    def test_post_and_open_quests(self):
        q = Quest("Clear the ruins", provider=self.provider)
        self.board.post(q)
        self.assertIn(q, self.board.open_quests)
        self.assertNotIn(q, self.board.taken_quests)

    def test_accept_via_board_moves_it_to_taken(self):
        q = Quest("Clear the ruins", provider=self.provider)
        self.board.post(q)
        self.board.accept(q, self.alice)
        self.assertIn(q, self.board.taken_quests)
        self.assertNotIn(q, self.board.open_quests)

    def test_accepting_unposted_quest_raises(self):
        q = Quest("Not posted", provider=self.provider)
        with self.assertRaises(ValueError):
            self.board.accept(q, self.alice)

    def test_remove_resolved_prunes_completed_quest(self):
        q = Quest("Clear the ruins", provider=self.provider)
        self.board.post(q)
        q.accept(self.alice)
        q.complete()

        self.board.remove_resolved()
        self.assertNotIn(q, self.board.posted_quests)

    def test_unpost(self):
        q = Quest("Clear the ruins", provider=self.provider)
        self.board.post(q)
        self.board.unpost(q)
        self.assertNotIn(q, self.board.posted_quests)


if __name__ == "__main__":
    unittest.main()
