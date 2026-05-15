"""
Mock Assessment 3 — In-Memory Key-Value Store
==============================================

RULES:
- 90 minutes
- No AI assistance
- Language docs and python_idioms.pdf allowed
- Run tests: python -m unittest kvstore_tests.py
- Run one level: python -m unittest kvstore_tests.Level1

Implement KVStoreImpl in kvstore_impl.py.

===========================================================================
SPEC
===========================================================================

Level 1: Basic get, set, delete.

  set(key: str, value: str) -> None
    Store the key-value pair. Overwrites any existing value for that key.

  get(key: str) -> str | None
    Return the value for key, or None if the key does not exist.

  delete(key: str) -> bool
    Remove the key. Return True if the key existed, False otherwise.

Level 2: Key queries.

  get_keys(prefix: str = "") -> list
    Return a sorted list of all stored keys.
    If prefix is given (non-empty), return only keys that start with prefix.

  count() -> int
    Return the number of keys currently stored.

Level 3: TTL (time-to-live).

  set_with_ttl(key: str, value: str, ttl: float) -> None
    Store the key-value pair. The key expires ttl seconds from now.
    After expiry, the key behaves as if it does not exist in all operations:
    get() returns None, delete() returns False, get_keys() excludes it,
    count() does not count it.
    Calling set() on a key that had a TTL replaces it and clears the TTL.
    Calling set_with_ttl() on an existing key replaces value and resets TTL.

  get_ttl(key: str) -> float | None
    If the key does not exist, has expired, or has no TTL: return None.
    If the key has an active TTL: return remaining seconds (float >= 0).

Level 4: Stats and rename.

  get_stats() -> dict
    Return:
      "live_keys" — count of non-expired keys
      "ttl_keys"  — count of live keys that currently have a TTL set

  rename(old_key: str, new_key: str) -> bool
    Rename old_key to new_key, preserving the value and any TTL.
    Return True if old_key existed (and was not expired), False otherwise.
    If new_key already exists, it is overwritten.
    If old_key does not exist or has expired, the store is unchanged.

Level 5: Transactions.

  begin() -> None
    Start a transaction. While a transaction is open:
      - set(), set_with_ttl(), and delete() are buffered (not applied yet).
      - get() checks the buffer first, then the main store.

  commit() -> bool
    Apply all buffered operations to the main store. End the transaction.
    Return True if a transaction was open, False otherwise.

  rollback() -> bool
    Discard all buffered operations without applying them. End the transaction.
    Return True if a transaction was open, False otherwise.

  Note: Only one transaction can be open at a time.

Level 6: Concurrent batch execution.

  execute_batch(operations: list) -> list
    Execute a list of operations in parallel using threads (one per operation).
    Each operation is a tuple:
      ("set",    key, value)  -> result is None
      ("get",    key)         -> result is str or None
      ("delete", key)         -> result is bool
    Return results in the same order as operations.
    Must be thread-safe.
===========================================================================
"""

import unittest
import time
from kvstore_impl import KVStoreImpl


class Level1(unittest.TestCase):

    def setUp(self):
        self.kv = KVStoreImpl()

    def test_set_and_get(self):
        self.kv.set("name", "Alice")
        self.assertEqual(self.kv.get("name"), "Alice")

    def test_get_missing(self):
        self.assertIsNone(self.kv.get("missing"))

    def test_overwrite(self):
        self.kv.set("x", "1")
        self.kv.set("x", "2")
        self.assertEqual(self.kv.get("x"), "2")

    def test_delete_existing(self):
        self.kv.set("x", "1")
        self.assertTrue(self.kv.delete("x"))
        self.assertIsNone(self.kv.get("x"))

    def test_delete_missing(self):
        self.assertFalse(self.kv.delete("missing"))

    def test_delete_twice(self):
        self.kv.set("x", "1")
        self.kv.delete("x")
        self.assertFalse(self.kv.delete("x"))


class Level2(unittest.TestCase):

    def setUp(self):
        self.kv = KVStoreImpl()
        self.kv.set("apple", "1")
        self.kv.set("apricot", "2")
        self.kv.set("banana", "3")
        self.kv.set("cherry", "4")

    def test_get_keys_all(self):
        self.assertEqual(self.kv.get_keys(), ["apple", "apricot", "banana", "cherry"])

    def test_get_keys_prefix(self):
        self.assertEqual(self.kv.get_keys("ap"), ["apple", "apricot"])

    def test_get_keys_no_match(self):
        self.assertEqual(self.kv.get_keys("z"), [])

    def test_get_keys_sorted(self):
        keys = self.kv.get_keys()
        self.assertEqual(keys, sorted(keys))

    def test_count(self):
        self.assertEqual(self.kv.count(), 4)

    def test_count_after_delete(self):
        self.kv.delete("apple")
        self.assertEqual(self.kv.count(), 3)

    def test_count_empty(self):
        self.assertEqual(KVStoreImpl().count(), 0)


class Level3(unittest.TestCase):

    def setUp(self):
        self.kv = KVStoreImpl()

    def test_ttl_get_before_expiry(self):
        self.kv.set_with_ttl("token", "abc", 1.0)
        self.assertEqual(self.kv.get("token"), "abc")

    def test_ttl_get_after_expiry(self):
        self.kv.set_with_ttl("token", "abc", 0.05)
        time.sleep(0.1)
        self.assertIsNone(self.kv.get("token"))

    def test_ttl_excluded_from_get_keys(self):
        self.kv.set("x", "1")
        self.kv.set_with_ttl("token", "abc", 0.05)
        time.sleep(0.1)
        self.assertNotIn("token", self.kv.get_keys())
        self.assertIn("x", self.kv.get_keys())

    def test_ttl_excluded_from_count(self):
        self.kv.set("x", "1")
        self.kv.set_with_ttl("token", "abc", 0.05)
        time.sleep(0.1)
        self.assertEqual(self.kv.count(), 1)

    def test_ttl_delete_after_expiry(self):
        self.kv.set_with_ttl("token", "abc", 0.05)
        time.sleep(0.1)
        self.assertFalse(self.kv.delete("token"))

    def test_set_clears_ttl(self):
        self.kv.set_with_ttl("x", "old", 0.05)
        self.kv.set("x", "new")
        time.sleep(0.1)
        self.assertEqual(self.kv.get("x"), "new")

    def test_get_ttl_active(self):
        self.kv.set_with_ttl("x", "1", 1.0)
        remaining = self.kv.get_ttl("x")
        self.assertIsNotNone(remaining)
        self.assertLessEqual(remaining, 1.0)
        self.assertGreater(remaining, 0.0)

    def test_get_ttl_no_ttl(self):
        self.kv.set("x", "1")
        self.assertIsNone(self.kv.get_ttl("x"))

    def test_get_ttl_missing(self):
        self.assertIsNone(self.kv.get_ttl("missing"))

    def test_get_ttl_expired(self):
        self.kv.set_with_ttl("x", "1", 0.05)
        time.sleep(0.1)
        self.assertIsNone(self.kv.get_ttl("x"))


class Level4(unittest.TestCase):

    def setUp(self):
        self.kv = KVStoreImpl()
        self.kv.set("a", "1")
        self.kv.set_with_ttl("b", "2", 1.0)
        self.kv.set_with_ttl("c", "3", 0.05)   # will expire

    def test_get_stats_live_keys(self):
        time.sleep(0.1)
        stats = self.kv.get_stats()
        self.assertEqual(stats["live_keys"], 2)   # a and b, c expired

    def test_get_stats_ttl_keys(self):
        time.sleep(0.1)
        stats = self.kv.get_stats()
        self.assertEqual(stats["ttl_keys"], 1)    # only b has active TTL

    def test_rename_basic(self):
        self.kv.set("x", "hello")
        self.assertTrue(self.kv.rename("x", "y"))
        self.assertEqual(self.kv.get("y"), "hello")
        self.assertIsNone(self.kv.get("x"))

    def test_rename_missing(self):
        self.assertFalse(self.kv.rename("missing", "y"))

    def test_rename_preserves_ttl(self):
        self.kv.set_with_ttl("src", "val", 1.0)
        self.kv.rename("src", "dst")
        remaining = self.kv.get_ttl("dst")
        self.assertIsNotNone(remaining)
        self.assertGreater(remaining, 0.0)

    def test_rename_expired_key(self):
        self.kv.set_with_ttl("x", "val", 0.05)
        time.sleep(0.1)
        self.assertFalse(self.kv.rename("x", "y"))
        self.assertIsNone(self.kv.get("y"))

    def test_rename_overwrites_destination(self):
        self.kv.set("src", "from")
        self.kv.set("dst", "to")
        self.kv.rename("src", "dst")
        self.assertEqual(self.kv.get("dst"), "from")


class Level5(unittest.TestCase):

    def setUp(self):
        self.kv = KVStoreImpl()
        self.kv.set("x", "original")

    def test_commit_applies_changes(self):
        self.kv.begin()
        self.kv.set("x", "updated")
        self.kv.commit()
        self.assertEqual(self.kv.get("x"), "updated")

    def test_rollback_discards_changes(self):
        self.kv.begin()
        self.kv.set("x", "updated")
        self.kv.rollback()
        self.assertEqual(self.kv.get("x"), "original")

    def test_get_sees_buffer(self):
        self.kv.begin()
        self.kv.set("x", "buffered")
        self.assertEqual(self.kv.get("x"), "buffered")
        self.kv.rollback()
        self.assertEqual(self.kv.get("x"), "original")

    def test_delete_commit(self):
        self.kv.begin()
        self.kv.delete("x")
        self.kv.commit()
        self.assertIsNone(self.kv.get("x"))

    def test_delete_rollback(self):
        self.kv.begin()
        self.kv.delete("x")
        self.kv.rollback()
        self.assertEqual(self.kv.get("x"), "original")

    def test_new_key_rollback(self):
        self.kv.begin()
        self.kv.set("new", "value")
        self.kv.rollback()
        self.assertIsNone(self.kv.get("new"))

    def test_commit_no_transaction(self):
        self.assertFalse(self.kv.commit())

    def test_rollback_no_transaction(self):
        self.assertFalse(self.kv.rollback())


class Level6(unittest.TestCase):

    def setUp(self):
        self.kv = KVStoreImpl()
        self.kv.set("a", "1")
        self.kv.set("b", "2")
        self.kv.set("c", "3")

    def test_batch_get(self):
        ops = [("get", "a"), ("get", "b"), ("get", "missing")]
        results = self.kv.execute_batch(ops)
        self.assertEqual(results, ["1", "2", None])

    def test_batch_set(self):
        ops = [("set", "x", "10"), ("set", "y", "20")]
        self.kv.execute_batch(ops)
        self.assertEqual(self.kv.get("x"), "10")
        self.assertEqual(self.kv.get("y"), "20")

    def test_batch_delete(self):
        ops = [("delete", "a"), ("delete", "missing")]
        results = self.kv.execute_batch(ops)
        self.assertTrue(results[0])
        self.assertFalse(results[1])

    def test_batch_order_preserved(self):
        ops = [("get", "a"), ("get", "b"), ("get", "c")]
        self.assertEqual(self.kv.execute_batch(ops), ["1", "2", "3"])

    def test_batch_thread_safety(self):
        ops = [("set", f"key{i}", str(i)) for i in range(50)]
        self.kv.execute_batch(ops)
        for i in range(50):
            self.assertEqual(self.kv.get(f"key{i}"), str(i))


if __name__ == "__main__":
    unittest.main(verbosity=2)
