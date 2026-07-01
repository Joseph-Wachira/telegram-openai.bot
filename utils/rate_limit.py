import time
from collections import defaultdict
from config import MAX_REQUESTS_PER_MINUTE

class RateLimiter:
    def __init__(self):
        self.user_requests = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        now = time.time()
        self.user_requests[user_id] = [
            t for t in self.user_requests[user_id] if now - t < 60
        ]
        if len(self.user_requests[user_id]) >= MAX_REQUESTS_PER_MINUTE:
            return False
        self.user_requests[user_id].append(now)
        return True

    def clear_user(self, user_id: int):
        self.user_requests.pop(user_id, None)

rate_limiter = RateLimiter()
