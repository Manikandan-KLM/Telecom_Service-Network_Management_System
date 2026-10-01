import time

from fastapi import HTTPException

from redis import Redis

from config import settings


redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


def check_rate_limit(
    key: str,
    limit: int | None = None,
    window: int | None = None
):

    limit = (
        limit
        if limit is not None
        else settings.RATE_LIMIT_REQUESTS
    )

    window = (
        window
        if window is not None
        else settings.RATE_LIMIT_WINDOW_SECONDS
    )

    redis_key = f"rate_limit:{key}"

    current = redis_client.incr(
        redis_key
    )

    if current == 1:

        redis_client.expire(
            redis_key,
            window
        )

    if current > limit:

        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )

    return True