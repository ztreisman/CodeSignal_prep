"""
Mock Assessment — Library System
=================================

You are building a library management system.

RULES:
- 90 minutes
- No AI assistance
- Language docs allowed (docs.python.org)
- Read ALL level specs before writing any code
- Run tests as you go: python -m unittest mock_tests.py
- Run one level at a time: python -m unittest mock_tests.Level1

Implement LibraryImpl in library_impl.py.

===========================================================================
SPEC
===========================================================================

Level 1: Add and retrieve books.

  add_book(title: str, author: str, copies: int) -> int
    Add a book to the library. copies is the total number of copies.
    Return the book_id (auto-assigned, starting at 1).

  get_book(book_id: int) -> dict | None
    Return {"id": int, "title": str, "author": str,
            "copies": int, "available": int}
    Return None if book_id does not exist.
    available starts equal to copies.

Level 2: Checkout and return books.

  checkout(book_id: int, user_id: str) -> bool
    Check out one copy of the book to the user.
    Return True if successful.
    Return False if: book not found, no copies available,
                     or user already has this book checked out.

  return_book(book_id: int, user_id: str) -> bool
    Return a copy of the book from the user.
    Return True if the user had this book checked out.
    Return False otherwise.

  get_user_books(user_id: str) -> list
    Return a sorted list of book_ids currently checked out by the user.
    Return [] if the user has no books checked out.

Level 3: Search and filter.

  search_by_author(author: str) -> list
    Return all books by the given author as a list of book dicts,
    sorted by title ascending.
    Return [] if no books found.

  get_available() -> list
    Return all books with at least one available copy,
    as a list of book dicts sorted by title ascending.

Level 4: Analytics.

  get_stats() -> dict
    Return:
      "total_books"  — number of distinct books
      "total_copies" — total copies across all books
      "checked_out"  — number of copies currently checked out
      "unique_users" — number of distinct users with at least one book

  get_popular(n: int) -> list
    Return the top n books by total number of successful checkouts
    (all-time, including books that have since been returned).
    Ties broken by title ascending.
    If fewer than n books exist, return all of them.
    Each entry: {"id": int, "title": str, "total_checkouts": int}

Level 5: Concurrent checkouts.

  batch_checkout(requests: list) -> list
    requests is a list of (book_id, user_id) tuples.
    Process all requests in parallel using threads.
    Return a list of bool results in the same order as requests.
    Must be thread-safe.
===========================================================================
"""

import unittest
from library_impl import LibraryImpl


class Level1(unittest.TestCase):

    def setUp(self):
        self.lib = LibraryImpl()

    def test_add_returns_sequential_ids(self):
        self.assertEqual(self.lib.add_book("Python Basics", "Alice", 3), 1)
        self.assertEqual(self.lib.add_book("Data Science", "Bob", 2), 2)

    def test_get_book_fields(self):
        self.lib.add_book("Python Basics", "Alice", 3)
        book = self.lib.get_book(1)
        self.assertEqual(book["id"], 1)
        self.assertEqual(book["title"], "Python Basics")
        self.assertEqual(book["author"], "Alice")
        self.assertEqual(book["copies"], 3)
        self.assertEqual(book["available"], 3)

    def test_get_book_not_found(self):
        self.assertIsNone(self.lib.get_book(99))

    def test_multiple_books_independent(self):
        self.lib.add_book("Book A", "Author X", 1)
        self.lib.add_book("Book B", "Author Y", 2)
        self.assertEqual(self.lib.get_book(1)["title"], "Book A")
        self.assertEqual(self.lib.get_book(2)["copies"], 2)


class Level2(unittest.TestCase):

    def setUp(self):
        self.lib = LibraryImpl()
        self.lib.add_book("Python Basics", "Alice", 2)   # id 1
        self.lib.add_book("Data Science", "Bob", 1)       # id 2

    def test_checkout_success(self):
        self.assertTrue(self.lib.checkout(1, "user1"))
        self.assertEqual(self.lib.get_book(1)["available"], 1)

    def test_checkout_no_copies(self):
        self.lib.checkout(2, "user1")
        self.assertFalse(self.lib.checkout(2, "user2"))

    def test_checkout_not_found(self):
        self.assertFalse(self.lib.checkout(99, "user1"))

    def test_checkout_same_book_twice_same_user(self):
        self.lib.checkout(1, "user1")
        self.assertFalse(self.lib.checkout(1, "user1"))

    def test_return_book_success(self):
        self.lib.checkout(1, "user1")
        self.assertTrue(self.lib.return_book(1, "user1"))
        self.assertEqual(self.lib.get_book(1)["available"], 2)

    def test_return_book_not_checked_out(self):
        self.assertFalse(self.lib.return_book(1, "user1"))

    def test_return_book_wrong_user(self):
        self.lib.checkout(1, "user1")
        self.assertFalse(self.lib.return_book(1, "user2"))

    def test_get_user_books(self):
        self.lib.checkout(1, "user1")
        self.lib.checkout(2, "user1")
        self.assertEqual(sorted(self.lib.get_user_books("user1")), [1, 2])

    def test_get_user_books_empty(self):
        self.assertEqual(self.lib.get_user_books("nobody"), [])

    def test_get_user_books_after_return(self):
        self.lib.checkout(1, "user1")
        self.lib.return_book(1, "user1")
        self.assertEqual(self.lib.get_user_books("user1"), [])


class Level3(unittest.TestCase):

    def setUp(self):
        self.lib = LibraryImpl()
        self.lib.add_book("Zebra Facts", "Alice", 2)    # id 1
        self.lib.add_book("Alpha Guide", "Alice", 1)    # id 2
        self.lib.add_book("Python Basics", "Bob", 3)   # id 3
        self.lib.checkout(1, "user1")
        self.lib.checkout(1, "user2")                   # Zebra Facts: 0 available

    def test_search_by_author_sorted(self):
        books = self.lib.search_by_author("Alice")
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0]["title"], "Alpha Guide")
        self.assertEqual(books[1]["title"], "Zebra Facts")

    def test_search_by_author_no_results(self):
        self.assertEqual(self.lib.search_by_author("Nobody"), [])

    def test_get_available_excludes_zero(self):
        titles = [b["title"] for b in self.lib.get_available()]
        self.assertNotIn("Zebra Facts", titles)
        self.assertIn("Alpha Guide", titles)
        self.assertIn("Python Basics", titles)

    def test_get_available_sorted_by_title(self):
        books = self.lib.get_available()
        titles = [b["title"] for b in books]
        self.assertEqual(titles, sorted(titles))


class Level4(unittest.TestCase):

    def setUp(self):
        self.lib = LibraryImpl()
        self.lib.add_book("Book A", "Author X", 3)   # id 1
        self.lib.add_book("Book B", "Author Y", 2)   # id 2
        self.lib.add_book("Book C", "Author X", 1)   # id 3

    def test_get_stats_empty(self):
        stats = self.lib.get_stats()
        self.assertEqual(stats["total_books"], 3)
        self.assertEqual(stats["total_copies"], 6)
        self.assertEqual(stats["checked_out"], 0)
        self.assertEqual(stats["unique_users"], 0)

    def test_get_stats_after_checkouts(self):
        self.lib.checkout(1, "user1")
        self.lib.checkout(2, "user1")
        self.lib.checkout(3, "user2")
        stats = self.lib.get_stats()
        self.assertEqual(stats["checked_out"], 3)
        self.assertEqual(stats["unique_users"], 2)

    def test_get_popular_order(self):
        self.lib.checkout(1, "user1")
        self.lib.return_book(1, "user1")
        self.lib.checkout(1, "user2")
        self.lib.checkout(2, "user3")
        top = self.lib.get_popular(2)
        self.assertEqual(top[0]["id"], 1)
        self.assertEqual(top[0]["total_checkouts"], 2)
        self.assertEqual(top[1]["id"], 2)

    def test_get_popular_tie_breaking(self):
        self.lib.checkout(1, "user1")
        self.lib.checkout(2, "user2")
        top = self.lib.get_popular(2)
        self.assertEqual(top[0]["title"], "Book A")
        self.assertEqual(top[1]["title"], "Book B")

    def test_get_popular_fewer_than_n(self):
        self.assertEqual(len(self.lib.get_popular(10)), 3)


class Level5(unittest.TestCase):

    def setUp(self):
        self.lib = LibraryImpl()
        for i in range(10):
            self.lib.add_book(f"Book {i}", "Author", 1)   # ids 1-10, 1 copy each

    def test_batch_checkout_all_succeed(self):
        requests = [(i + 1, f"user{i}") for i in range(10)]
        results = self.lib.batch_checkout(requests)
        self.assertEqual(len(results), 10)
        self.assertTrue(all(results))

    def test_batch_checkout_thread_safety(self):
        # 1 copy of book 1; 5 users compete — exactly 1 should succeed
        requests = [(1, f"user{i}") for i in range(5)]
        results = self.lib.batch_checkout(requests)
        self.assertEqual(sum(results), 1)

    def test_batch_checkout_order_preserved(self):
        requests = [(i + 1, "user0") for i in range(10)]
        results = self.lib.batch_checkout(requests)
        self.assertEqual(len(results), 10)
        self.assertIsInstance(results[0], bool)


if __name__ == "__main__":
    unittest.main(verbosity=2)
