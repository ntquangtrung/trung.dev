from django.core.cache import cache

CACHE_TIMEOUT = 60 * 60  # 1 hour
CACHE_PREFIXES = {
    "PROJECTS": "projects",
}


class RedisCacheHandler:
    def __init__(self, prefix: str, timeout: int = CACHE_TIMEOUT):
        if prefix is None or prefix not in CACHE_PREFIXES.values():
            raise ValueError(
                f"Invalid prefix '{prefix}'. Must be one of {list(CACHE_PREFIXES.values())}"
            )
        self.prefix = prefix
        self.timeout = timeout

    def _key(self, name: str) -> str:
        return f"{self.prefix}:{name}"

    def get(self, name: str):
        return cache.get(self._key(name))

    def set_cache(self, name: str, value, timeout=None):
        if timeout is None:
            timeout = self.timeout
        cache.set(self._key(name), value, timeout)

    def delete(self, name: str):
        return cache.delete(self._key(name))

    def get_or_set(self, name: str, default_value, timeout=None):
        if timeout is None:
            timeout = self.timeout
        return cache.get_or_set(self._key(name), default_value, timeout)

    def get_all_keys(self) -> list[str]:
        pattern = f"{self.prefix}:*"
        return cache.keys(pattern)

    def clear_all(self):
        cache.clear()

    def increase(self, name: str, amount: int = 1):
        return cache.incr(self._key(name), amount)
