import threading


class Library:
    """Base class — do not modify."""

    def add_book(self, title: str, author: str, copies: int) -> int:
        raise NotImplementedError

    def get_book(self, book_id: int):
        return None

    def checkout(self, book_id: int, user_id: str) -> bool:
        return False

    def return_book(self, book_id: int, user_id: str) -> bool:
        return False

    def get_user_books(self, user_id: str) -> list:
        return []

    def search_by_author(self, author: str) -> list:
        return []

    def get_available(self) -> list:
        return []

    def get_stats(self) -> dict:
        return {"total_books": 0, "total_copies": 0, "checked_out": 0, "unique_users": 0}

    def get_popular(self, n: int) -> list:
        return []

    def batch_checkout(self, requests: list) -> list:
        return []


class LibraryImpl(Library):

    def __init__(self):
        self.library = {}
        self.next_book_id = 1
        self.users = []
        self.lock = threading.Lock()

# level 1

    def add_book(self, title, author, copies):
        book_id = self.next_book_id
        self.next_book_id += 1
        self.library[book_id] ={"id": book_id, "title": title, "author": author,
            "copies": copies, "available": copies, "checkout":[], "total_checkouts":0}
        return book_id
    
    def get_book(self, book_id: int) -> dict | None:
        return self.library.get(book_id)

# level 2

    def checkout(self, book_id: int, user_id: str) -> bool:
        if self.get_book(book_id) is not None:
            if self.get_book(book_id)["available"] > 0:
                if user_id not in self.get_book(book_id)["checkout"]:
                    self.get_book(book_id)["checkout"].append(user_id)
                    self.get_book(book_id)["available"] -= 1
                    self.get_book(book_id)["total_checkouts"] += 1
                    return True
        return False        

    def return_book(self, book_id: int, user_id: str) -> bool:
        if self.get_book(book_id) is not None:
            if user_id in self.get_book(book_id)["checkout"]:
                self.get_book(book_id)["checkout"].remove(user_id)
                self.get_book(book_id)["available"] += 1
                return True
        return False
    
    def get_user_books(self, user_id: str) -> list:
        return sorted([b["id"] for b in self.library.values() if user_id in b["checkout"]])
    
# level 3

    def search_by_author(self, author: str) -> list:
        return sorted([b for b in self.library.values() if b["author"]==author], key=lambda x:x["title"])

    def get_available(self) -> list:
        return sorted([b for b in self.library.values() if b["available"]>0], key=lambda x:x["title"])
    
# level 4
    
    def get_stats(self) -> dict:
        total_books = len(self.library)
        total_copies = sum([b["copies"] for b in self.library.values()])
        checked_out = total_copies - sum([b["available"] for b in self.library.values()])
        all_checkouts = [b["checkout"] for b in self.library.values()]
        unique_users = len({user for user_checkout in all_checkouts for user in user_checkout})
        return {"total_books":total_books, "total_copies":total_copies, "checked_out":checked_out, "unique_users":unique_users}

    def get_popular(self, n: int) -> list:
        popular_books = sorted(self.library.items(), key=lambda x: (-x[1]["total_checkouts"], x[1]["title"]))[:n]
        popular_books_summary = [{"id":b[0], "title":b[1]["title"], "total_checkouts":b[1]["total_checkouts"]} for b in popular_books]
        return popular_books_summary


# level 5

    def batch_checkout(self, requests: list) -> list:

        current_request = 0
        results = [None]*len(requests)

        def worker():
            nonlocal current_request

            while True:
                with self.lock:
                    if current_request >= len(requests):
                        break
                    i = current_request
                    current_request += 1
                results[i] = self.checkout(requests[i][0], requests[i][1])

        threads = []

        for _ in range(len(requests)):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        return results

   