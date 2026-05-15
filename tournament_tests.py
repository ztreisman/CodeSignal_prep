"""
Mock Assessment 2 — Tournament Leaderboard
==========================================

RULES:
- 90 minutes
- No AI assistance
- Language docs allowed (docs.python.org)
- Read ALL level specs before writing any code
- Run tests: python -m unittest tournament_tests.py
- Run one level: python -m unittest tournament_tests.Level1

Implement TournamentImpl in tournament_impl.py.

===========================================================================
SPEC
===========================================================================

Level 1: Register and retrieve players.

  add_player(name: str) -> int
    Register a new player. Return the player_id (auto-assigned, starting at 1).

  get_player(player_id: int) -> dict | None
    Return {"id": int, "name": str, "score": int, "wins": int, "losses": int}
    Return None if player_id does not exist.
    score, wins, and losses all start at 0.

Level 2: Record match results and rankings.

  record_result(winner_id: int, loser_id: int, points: int) -> bool
    Record a match result.
    The winner's score increases by points; their win count increases by 1.
    The loser's loss count increases by 1. The loser's score does not change.
    Return True if both players exist, False otherwise.
    If False, no state is changed.

  get_ranking(n: int = None) -> list
    Return players sorted by score descending, ties broken by name ascending.
    Each entry is a full player dict.
    If n is given, return only the top n players.
    If n is None, return all players.

Level 3: Filter and search.

  get_undefeated() -> list
    Return players with at least one win and zero losses,
    sorted by score descending.
    Players who have never played are excluded.

  get_by_score_range(min_score: int, max_score: int) -> list
    Return players whose score is between min_score and max_score (inclusive),
    sorted by score descending, ties broken by name ascending.

Level 4: Analytics.

  get_stats() -> dict
    Return:
      "total_players"  — number of registered players
      "total_matches"  — total number of recorded match results
      "total_points"   — total points awarded across all matches
      "average_score"  — mean score across all players, rounded to 2 decimal places
                         (0.0 if no players)

  get_top_scorer() -> dict | None
    Return the player dict of the player with the highest score.
    If multiple players are tied, return the one whose name comes first alphabetically.
    Return None if no players are registered.

Level 5: Concurrent result recording.

  record_results_parallel(results: list) -> list
    results is a list of (winner_id, loser_id, points) tuples.
    Process all results in parallel using threads.
    Return a list of bool results in the same order as input.
    Must be thread-safe: no score updates may be lost.
===========================================================================
"""

import unittest
from tournament_impl import TournamentImpl


class Level1(unittest.TestCase):

    def setUp(self):
        self.t = TournamentImpl()

    def test_add_player_sequential_ids(self):
        self.assertEqual(self.t.add_player("Alice"), 1)
        self.assertEqual(self.t.add_player("Bob"), 2)
        self.assertEqual(self.t.add_player("Carol"), 3)

    def test_get_player_fields(self):
        self.t.add_player("Alice")
        p = self.t.get_player(1)
        self.assertEqual(p["id"], 1)
        self.assertEqual(p["name"], "Alice")
        self.assertEqual(p["score"], 0)
        self.assertEqual(p["wins"], 0)
        self.assertEqual(p["losses"], 0)

    def test_get_player_not_found(self):
        self.assertIsNone(self.t.get_player(99))

    def test_multiple_players_independent(self):
        self.t.add_player("Alice")
        self.t.add_player("Bob")
        self.assertEqual(self.t.get_player(1)["name"], "Alice")
        self.assertEqual(self.t.get_player(2)["name"], "Bob")


class Level2(unittest.TestCase):

    def setUp(self):
        self.t = TournamentImpl()
        self.t.add_player("Alice")   # id 1
        self.t.add_player("Bob")     # id 2
        self.t.add_player("Carol")   # id 3

    def test_record_result_returns_true(self):
        self.assertTrue(self.t.record_result(1, 2, 10))

    def test_record_result_winner_score(self):
        self.t.record_result(1, 2, 10)
        self.assertEqual(self.t.get_player(1)["score"], 10)
        self.assertEqual(self.t.get_player(1)["wins"], 1)

    def test_record_result_loser_unchanged_score(self):
        self.t.record_result(1, 2, 10)
        self.assertEqual(self.t.get_player(2)["score"], 0)
        self.assertEqual(self.t.get_player(2)["losses"], 1)

    def test_record_result_accumulates(self):
        self.t.record_result(1, 2, 10)
        self.t.record_result(1, 3, 15)
        self.assertEqual(self.t.get_player(1)["score"], 25)
        self.assertEqual(self.t.get_player(1)["wins"], 2)

    def test_record_result_invalid_player(self):
        self.assertFalse(self.t.record_result(1, 99, 10))
        self.assertEqual(self.t.get_player(1)["score"], 0)

    def test_get_ranking_order(self):
        self.t.record_result(2, 1, 20)
        self.t.record_result(3, 1, 10)
        ranking = self.t.get_ranking()
        self.assertEqual(ranking[0]["name"], "Bob")
        self.assertEqual(ranking[1]["name"], "Carol")
        self.assertEqual(ranking[2]["name"], "Alice")

    def test_get_ranking_tie_breaking(self):
        self.t.record_result(1, 3, 10)
        self.t.record_result(2, 3, 10)
        ranking = self.t.get_ranking()
        self.assertEqual(ranking[0]["name"], "Alice")
        self.assertEqual(ranking[1]["name"], "Bob")

    def test_get_ranking_top_n(self):
        self.t.record_result(1, 3, 30)
        self.t.record_result(2, 3, 20)
        top2 = self.t.get_ranking(2)
        self.assertEqual(len(top2), 2)
        self.assertEqual(top2[0]["name"], "Alice")

    def test_get_ranking_n_larger_than_players(self):
        self.assertEqual(len(self.t.get_ranking(10)), 3)


class Level3(unittest.TestCase):

    def setUp(self):
        self.t = TournamentImpl()
        self.t.add_player("Alice")   # id 1
        self.t.add_player("Bob")     # id 2
        self.t.add_player("Carol")   # id 3
        self.t.add_player("Dave")    # id 4
        self.t.record_result(1, 2, 30)   # Alice: 30pts 1W 0L
        self.t.record_result(3, 2, 20)   # Carol: 20pts 1W 0L
        self.t.record_result(2, 4, 10)   # Bob:   10pts 1W 2L
        # Dave: 0pts 0W 1L

    def test_get_undefeated_excludes_never_played(self):
        # Dave has 0 wins and 1 loss -- excluded
        # Bob has wins but also losses -- excluded
        names = [p["name"] for p in self.t.get_undefeated()]
        self.assertNotIn("Dave", names)
        self.assertNotIn("Bob", names)

    def test_get_undefeated_sorted_by_score(self):
        result = self.t.get_undefeated()
        self.assertEqual(result[0]["name"], "Alice")
        self.assertEqual(result[1]["name"], "Carol")

    def test_get_by_score_range(self):
        result = self.t.get_by_score_range(15, 35)
        scores = [p["score"] for p in result]
        self.assertIn(30, scores)
        self.assertIn(20, scores)
        self.assertNotIn(10, scores)

    def test_get_by_score_range_inclusive(self):
        result = self.t.get_by_score_range(10, 20)
        scores = [p["score"] for p in result]
        self.assertIn(10, scores)
        self.assertIn(20, scores)

    def test_get_by_score_range_sorted(self):
        result = self.t.get_by_score_range(0, 100)
        scores = [p["score"] for p in result]
        self.assertEqual(scores, sorted(scores, reverse=True))


class Level4(unittest.TestCase):

    def setUp(self):
        self.t = TournamentImpl()
        self.t.add_player("Alice")   # id 1
        self.t.add_player("Bob")     # id 2
        self.t.add_player("Carol")   # id 3

    def test_get_stats_no_matches(self):
        stats = self.t.get_stats()
        self.assertEqual(stats["total_players"], 3)
        self.assertEqual(stats["total_matches"], 0)
        self.assertEqual(stats["total_points"], 0)
        self.assertEqual(stats["average_score"], 0.0)

    def test_get_stats_after_matches(self):
        self.t.record_result(1, 2, 30)
        self.t.record_result(3, 2, 20)
        stats = self.t.get_stats()
        self.assertEqual(stats["total_matches"], 2)
        self.assertEqual(stats["total_points"], 50)
        self.assertAlmostEqual(stats["average_score"], round(50/3, 2))

    def test_get_top_scorer(self):
        self.t.record_result(1, 2, 30)
        self.t.record_result(3, 2, 20)
        top = self.t.get_top_scorer()
        self.assertEqual(top["name"], "Alice")

    def test_get_top_scorer_tie(self):
        self.t.record_result(1, 3, 20)
        self.t.record_result(2, 3, 20)
        top = self.t.get_top_scorer()
        self.assertEqual(top["name"], "Alice")   # alphabetically first

    def test_get_top_scorer_no_players(self):
        empty = TournamentImpl()
        self.assertIsNone(empty.get_top_scorer())


class Level5(unittest.TestCase):

    def setUp(self):
        self.t = TournamentImpl()
        self.t.add_player("Alice")   # id 1
        self.t.add_player("Bob")     # id 2

    def test_parallel_results_all_true(self):
        results = [(1, 2, i + 1) for i in range(10)]
        out = self.t.record_results_parallel(results)
        self.assertEqual(len(out), 10)
        self.assertTrue(all(out))

    def test_parallel_results_invalid(self):
        results = [(1, 2, 10), (1, 99, 5), (2, 1, 8)]
        out = self.t.record_results_parallel(results)
        self.assertFalse(out[1])

    def test_parallel_no_lost_updates(self):
        # 20 concurrent wins for Alice against Bob, points 1..20
        # total should be exactly sum(1..20) = 210
        results = [(1, 2, i + 1) for i in range(20)]
        self.t.record_results_parallel(results)
        self.assertEqual(self.t.get_player(1)["score"], 210)
        self.assertEqual(self.t.get_player(1)["wins"], 20)

    def test_parallel_order_preserved(self):
        results = [(1, 2, 10), (2, 1, 20), (1, 2, 5)]
        out = self.t.record_results_parallel(results)
        self.assertEqual(len(out), 3)
        self.assertIsInstance(out[0], bool)


if __name__ == "__main__":
    unittest.main(verbosity=2)
