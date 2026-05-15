# Problem 11

import threading


class MessageBoard:
    """Base class — do not modify."""

    def post_message(self, author: str, content: str) -> int:
        raise NotImplementedError

    def get_message(self, message_id: int):
        return None

    def like_message(self, message_id: int):
        return None

    def get_top_messages(self, n: int) -> list:
        return []

    def get_author_stats(self, author: str) -> dict:
        return {"post_count": 0, "total_likes": 0}

    def process_actions(self, actions: list) -> list:
        return []


class MessageBoardImpl(MessageBoard):

    def __init__(self):
        self.messages = {}
        self.next_id = 1
        self.lock = threading.Lock()
   
    # --- Level 1 ---

    def post_message(self, author: str, content: str) -> int:
        message_id = self.next_id
        self.messages[message_id] = {"id": message_id, "author": author, "content": content, "likes": 0} 
        self.next_id += 1
        return message_id   

    def get_message(self, message_id: int):
        return self.messages.get(message_id)

    # --- Level 2 ---

    def like_message(self, message_id: int):
        if message_id in self.messages:
            self.messages[message_id]["likes"] += 1
            return self.messages[message_id]["likes"]
        else:
            return None

    def get_top_messages(self, n: int) -> list:
        sorted_messages = sorted(self.messages.values(), key=lambda m: (-m["likes"], m["id"]))
        return sorted_messages[:n]

    def get_author_stats(self, author: str) -> dict:
        author_messages = [m for m in self.messages.values() if m["author"]==author]
        post_count = len(author_messages)
        total_likes = sum(m["likes"] for m in author_messages)
        return {"post_count": post_count, "total_likes": total_likes}

    # --- Level 3 ---


    def process_actions(self, actions: list) -> list:
        results = [None]*len(actions)

        def process_action(i, action):
            with self.lock:
            
                if action[0] == "post":
                    _, author, content = action
                    results[i] = self.post_message(author, content)
                elif action[0] == "like":
                    _, message_id = action
                    results[i] = self.like_message(message_id)
        threads = []
        for i, action in enumerate(actions):
            t = threading.Thread(target=process_action, args=(i, action))
            t.start()
            threads.append(t)
        for t in threads:            
            t.join()

        return results
