"""
Problem 11 — Message Board
==========================

Implement a MessageBoardImpl class in message_board_impl.py.

SPEC
----

Level 1: Post and retrieve messages.

  post_message(author: str, content: str) -> int
    Post a message. Return the message_id (auto-assigned, starting at 1).

  get_message(message_id: int) -> dict | None
    Return the message as a dict:
      {"id": int, "author": str, "content": str, "likes": int}
    Return None if message_id does not exist.

Level 2: Likes, ranking, and author stats.

  like_message(message_id: int) -> int | None
    Increment the like count on the message.
    Return the new like count.
    Return None if message_id does not exist.

  get_top_messages(n: int) -> list
    Return the top n messages sorted by likes descending.
    Break ties by message_id ascending.
    If fewer than n messages exist, return all of them.

  get_author_stats(author: str) -> dict
    Return {"post_count": int, "total_likes": int} for the given author.
    If the author has no posts, return {"post_count": 0, "total_likes": 0}.

Level 3: Concurrent action processing.

  process_actions(actions: list) -> list
    Process a list of actions using threads (one thread per action).
    Each action is a tuple:
      ("post", author, content)  -> result is the new message_id (int)
      ("like", message_id)       -> result is the new like count (int | None)
    Return a list of results in the SAME ORDER as the input actions.
    Implementation must be thread-safe.

Run tests:
  python -m unittest problem_11_tests.py        # all levels
  python -m unittest problem_11_tests.Level1    # one level
"""

import unittest
import threading
from message_board_impl import MessageBoardImpl


class Level1(unittest.TestCase):

    def setUp(self):
        self.mb = MessageBoardImpl()

    def test_post_returns_sequential_ids(self):
        self.assertEqual(self.mb.post_message("Alice", "Hello"), 1)
        self.assertEqual(self.mb.post_message("Bob", "World"), 2)
        self.assertEqual(self.mb.post_message("Alice", "Again"), 3)

    def test_get_message_fields(self):
        self.mb.post_message("Alice", "Hello world")
        msg = self.mb.get_message(1)
        self.assertEqual(msg["id"], 1)
        self.assertEqual(msg["author"], "Alice")
        self.assertEqual(msg["content"], "Hello world")
        self.assertEqual(msg["likes"], 0)

    def test_get_message_not_found(self):
        self.assertIsNone(self.mb.get_message(99))

    def test_get_message_not_found_empty_board(self):
        self.assertIsNone(self.mb.get_message(1))

    def test_multiple_messages_independent(self):
        self.mb.post_message("Alice", "First")
        self.mb.post_message("Bob", "Second")
        self.assertEqual(self.mb.get_message(1)["author"], "Alice")
        self.assertEqual(self.mb.get_message(2)["author"], "Bob")


class Level2(unittest.TestCase):

    def setUp(self):
        self.mb = MessageBoardImpl()
        self.mb.post_message("Alice", "First post")    # id 1
        self.mb.post_message("Bob", "Second post")     # id 2
        self.mb.post_message("Alice", "Third post")    # id 3

    def test_like_increments(self):
        self.assertEqual(self.mb.like_message(1), 1)
        self.assertEqual(self.mb.like_message(1), 2)
        self.assertEqual(self.mb.like_message(1), 3)

    def test_like_not_found(self):
        self.assertIsNone(self.mb.like_message(99))

    def test_like_reflects_in_get_message(self):
        self.mb.like_message(2)
        self.mb.like_message(2)
        self.assertEqual(self.mb.get_message(2)["likes"], 2)

    def test_get_top_messages_order(self):
        self.mb.like_message(2)
        self.mb.like_message(2)
        self.mb.like_message(1)
        # msg2: 2 likes, msg1: 1 like, msg3: 0 likes
        top = self.mb.get_top_messages(3)
        self.assertEqual([m["id"] for m in top], [2, 1, 3])

    def test_get_top_messages_tie_breaking(self):
        # msg1 and msg2 each get 1 like — tie broken by id ascending
        self.mb.like_message(1)
        self.mb.like_message(2)
        top = self.mb.get_top_messages(2)
        self.assertEqual(top[0]["id"], 1)
        self.assertEqual(top[1]["id"], 2)

    def test_get_top_messages_fewer_than_n(self):
        top = self.mb.get_top_messages(100)
        self.assertEqual(len(top), 3)

    def test_get_author_stats(self):
        self.mb.like_message(1)
        self.mb.like_message(3)
        self.mb.like_message(3)
        stats = self.mb.get_author_stats("Alice")
        self.assertEqual(stats["post_count"], 2)
        self.assertEqual(stats["total_likes"], 3)

    def test_get_author_stats_no_posts(self):
        stats = self.mb.get_author_stats("Nobody")
        self.assertEqual(stats["post_count"], 0)
        self.assertEqual(stats["total_likes"], 0)

    def test_get_author_stats_single_author(self):
        self.mb.like_message(2)
        stats = self.mb.get_author_stats("Bob")
        self.assertEqual(stats["post_count"], 1)
        self.assertEqual(stats["total_likes"], 1)


class Level3(unittest.TestCase):

    def setUp(self):
        self.mb = MessageBoardImpl()

    def test_process_post_actions(self):
        actions = [
            ("post", "Alice", "Hello"),
            ("post", "Bob", "World"),
            ("post", "Alice", "Again"),
        ]
        results = self.mb.process_actions(actions)
        self.assertEqual(results, [1, 2, 3])

    def test_process_like_actions(self):
        self.mb.post_message("Alice", "Hello")
        actions = [
            ("like", 1),
            ("like", 1),
            ("like", 99),   # not found
        ]
        results = self.mb.process_actions(actions)
        # first two are like counts (positive ints), third is None
        self.assertIsInstance(results[0], int)
        self.assertIsInstance(results[1], int)
        self.assertIsNone(results[2])

    def test_process_actions_order_preserved(self):
        # Results must be in the same order as input, even with threading
        actions = [("post", f"user{i}", f"msg{i}") for i in range(10)]
        results = self.mb.process_actions(actions)
        self.assertEqual(results, list(range(1, 11)))

    def test_process_actions_thread_safety(self):
        # 50 concurrent posts must all produce unique IDs
        actions = [("post", f"user{i}", f"content{i}") for i in range(50)]
        results = self.mb.process_actions(actions)
        self.assertEqual(len(results), 50)
        self.assertEqual(len(set(results)), 50)  # all unique

    def test_final_state_consistent(self):
        # After concurrent posts, get_message works for all of them
        actions = [("post", "Alice", f"msg{i}") for i in range(5)]
        ids = self.mb.process_actions(actions)
        for mid in ids:
            self.assertIsNotNone(self.mb.get_message(mid))


if __name__ == "__main__":
    unittest.main(verbosity=2)
