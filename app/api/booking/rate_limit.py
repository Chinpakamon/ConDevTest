import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.core.settings import settings

_hits: dict[str, deque[float]] = defaultdict(deque)


async def check_post_rate_limit(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window_start = now - 60
    hits = _hits[client]
    while hits and hits[0] < window_start:
        hits.popleft()
    if len(hits) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many booking requests, please retry later",
        )
    hits.append(now)


def reset_rate_limit() -> None:
    _hits.clear()
