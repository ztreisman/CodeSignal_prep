import threading
import time


class KVStore:
    """Base class — do not modify."""

    def set(self, key: str, value: str) -> None:
        raise NotImplementedError

    def get(self, key: str):
        return None

    def delete(self, key: str) -> bool:
        return False

    def get_keys(self, prefix: str = "") -> list:
        return []

    def count(self) -> int:
        return 0

    def set_with_ttl(self, key: str, value: str, ttl: float) -> None:
        raise NotImplementedError

    def get_ttl(self, key: str):
        return None

    def get_stats(self) -> dict:
        return {"live_keys": 0, "ttl_keys": 0}

    def rename(self, old_key: str, new_key: str) -> bool:
        return False

    def begin(self) -> None:
        raise NotImplementedError

    def commit(self) -> bool:
        return False

    def rollback(self) -> bool:
        return False

    def execute_batch(self, operations: list) -> list:
        return []


class KVStoreImpl(KVStore):

    def __init__(self):
        pass
