import time
from typing import Dict, List

from app.config.settings import settings

class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
    
    async def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limits."""
        current_time = time.time()
        window_start = current_time - settings.RATE_LIMIT_WINDOW
        
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        if len(self.requests[identifier]) >= settings.RATE_LIMIT_REQUESTS:
            return False
        
        self.requests[identifier].append(current_time)
        return True

rate_limiter = RateLimiter()