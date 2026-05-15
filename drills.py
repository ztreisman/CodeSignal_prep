"""
Focused Drills — run with: python -m unittest drills.py
Each drill is self-contained. Implement the stub above its test class.
"""

import unittest
import queue
import threading


# =============================================================================
# Drill 1: String parsing
# =============================================================================
# parse_records(text) takes a multi-line string where each line has the form:
#   "name:score:category"
# and returns a list of dicts:
#   [{"name": str, "score": int, "category": str}, ...]
# sorted by score descending, ties broken by name alphabetically.
# Skip any blank lines.
#
# Example:
#   text = "Alice:85:math\nBob:92:science\n\nCarol:85:math"
#   parse_records(text)
#   → [{"name": "Bob",   "score": 92, "category": "science"},
#      {"name": "Alice", "score": 85, "category": "math"},
#      {"name": "Carol", "score": 85, "category": "math"}]
#
# Hints: str.split("\n"), str.split(":"), int(), sorted() with a tuple key

def parse_records(text: str) -> list:
    lines = text.split("\n")
    lines = [l for l in lines if l != ""]
    records = []
    for l in lines:
        name, score, category = l.split(":")
        records.append({"name":name, "score":int(score), "category":category})
    records = sorted(records, key=lambda x: (-x["score"], x["name"]))  
    return records  



class Drill1(unittest.TestCase):

    def test_basic(self):
        text = "Alice:85:math\nBob:92:science\nCarol:78:math"
        result = parse_records(text)
        self.assertEqual(result[0]["name"], "Bob")
        self.assertEqual(result[0]["score"], 92)
        self.assertEqual(result[1]["name"], "Alice")
        self.assertEqual(result[2]["name"], "Carol")

    def test_score_is_int(self):
        result = parse_records("Alice:85:math")
        self.assertIsInstance(result[0]["score"], int)

    def test_tie_broken_by_name(self):
        text = "Zara:85:math\nAlice:85:science"
        result = parse_records(text)
        self.assertEqual(result[0]["name"], "Alice")
        self.assertEqual(result[1]["name"], "Zara")

    def test_skips_blank_lines(self):
        text = "Alice:85:math\n\nBob:92:science\n"
        result = parse_records(text)
        self.assertEqual(len(result), 2)


# =============================================================================
# Drill 2: String formatting
# =============================================================================
# format_report(records) takes a list of dicts (same shape as Drill 1 output)
# and returns a single string — one line per record — formatted as:
#   "Name: {name:<12} Score: {score:>3}  Category: {category}"
# Lines joined by newlines (no trailing newline).
#
# Example:
#   records = [{"name": "Bob", "score": 92, "category": "science"},
#              {"name": "Alice", "score": 85, "category": "math"}]
#   print(format_report(records))
#   Name: Bob          Score:  92  Category: science
#   Name: Alice        Score:  85  Category: math
#
# Hints: f"{value:<12}" left-aligns in 12 chars, f"{value:>3}" right-aligns in 3
#        "\n".join(list_of_strings)

def format_report(records: list) -> str:
    report = []
    for r in records:
        report.append(f"Name: {r['name']:<12} Score: {r['score']:>3} Category: {r['category']}\n")
    return "".join(report).rstrip()


class Drill2(unittest.TestCase):

    def test_output_is_string(self):
        records = [{"name": "Alice", "score": 85, "category": "math"}]
        self.assertIsInstance(format_report(records), str)

    def test_one_line_per_record(self):
        records = [
            {"name": "Bob",   "score": 92, "category": "science"},
            {"name": "Alice", "score": 85, "category": "math"},
        ]
        lines = format_report(records).split("\n")
        self.assertEqual(len(lines), 2)

    def test_line_content(self):
        records = [{"name": "Bob", "score": 92, "category": "science"}]
        line = format_report(records)
        self.assertIn("Bob", line)
        self.assertIn("92", line)
        self.assertIn("science", line)

    def test_no_trailing_newline(self):
        records = [{"name": "Alice", "score": 85, "category": "math"}]
        self.assertFalse(format_report(records).endswith("\n"))


# =============================================================================
# Drill 3: any() and all()
# =============================================================================
# Three one-liner functions. No loops allowed — use any() or all().
#
# passed_all(scores, threshold) — True if every score >= threshold
# any_failing(scores, threshold) — True if any score < threshold
# all_same_category(records, category) — True if every record's "category"
#                                        equals the given category

def passed_all(scores: list, threshold: int) -> bool:
    return all(s >= threshold for s in scores)

def any_failing(scores: list, threshold: int) -> bool:
    return any(s<threshold for s in scores)

def all_same_category(records: list, category: str) -> bool:
    return all(r["category"] == category for r in records)


class Drill3(unittest.TestCase):

    def test_passed_all_true(self):
        self.assertTrue(passed_all([80, 90, 75], 70))

    def test_passed_all_false(self):
        self.assertFalse(passed_all([80, 65, 90], 70))

    def test_any_failing_true(self):
        self.assertTrue(any_failing([80, 65, 90], 70))

    def test_any_failing_false(self):
        self.assertFalse(any_failing([80, 90, 75], 70))

    def test_all_same_category_true(self):
        records = [{"category": "math"}, {"category": "math"}]
        self.assertTrue(all_same_category(records, "math"))

    def test_all_same_category_false(self):
        records = [{"category": "math"}, {"category": "science"}]
        self.assertFalse(all_same_category(records, "math"))


# =============================================================================
# Drill 4: queue.Queue worker pool
# =============================================================================
# This is an alternative threading pattern using queue.Queue instead of a
# manual lock + shared list.
#
# Implement process_with_workers(items, fn, n_workers) that:
# - Takes a list of items, a function fn, and a number of workers
# - Puts all items into a queue.Queue
# - Spawns n_workers threads; each worker pulls items from the queue and
#   calls fn(item), storing the result
# - Returns a dict mapping each item to fn(item)
# - Workers stop when the queue is empty (queue.Queue raises queue.Empty
#   when get(block=False) is called on an empty queue)
#
# queue.Queue basics:
#   q = queue.Queue()
#   q.put(item)          # add item
#   q.get(block=False)   # get item, raises queue.Empty if empty
#
# Note: queue.Queue is already thread-safe — you do NOT need a lock.
# Results dict: use a lock since multiple threads write to it.
#
# Example:
#   result = process_with_workers([1, 2, 3, 4], lambda x: x * x, 2)
#   → {1: 1, 2: 4, 3: 9, 4: 16}  (order of processing not guaranteed)

def process_with_workers(items: list, fn, n_workers: int) -> dict:
    
    lock = threading.Lock()
    q = queue.Queue()
    results = {}
    
    for item in items:
        q.put(item)
    
    def worker():
        while True:
            try:
                item = q.get(block=False)
            except queue.Empty:
                break
            value = fn(item)
            with lock:
                results[item] = value
    
    threads = []
    for _ in range(n_workers):
        t =threading.Thread(target=worker)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    
    return results


class Drill4(unittest.TestCase):

    def test_basic(self):
        result = process_with_workers([1, 2, 3, 4], lambda x: x * x, 2)
        self.assertEqual(result, {1: 1, 2: 4, 3: 9, 4: 16})

    def test_all_items_processed(self):
        items = list(range(20))
        result = process_with_workers(items, lambda x: x + 1, 4)
        self.assertEqual(len(result), 20)
        for i in items:
            self.assertEqual(result[i], i + 1)

    def test_single_worker(self):
        result = process_with_workers(["a", "b", "c"], str.upper, 1)
        self.assertEqual(result, {"a": "A", "b": "B", "c": "C"})

    def test_more_workers_than_items(self):
        result = process_with_workers([1, 2], lambda x: x * 2, 10)
        self.assertEqual(result, {1: 2, 2: 4})


if __name__ == "__main__":
    unittest.main(verbosity=2)
