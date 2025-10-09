import redis

from core.config import config

# print("=== cache.py started ===")

redis_session_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    username="session",
    password=config.REDIS_SESSION_PASSWORD,
    db=config.REDIS_SESSION_DB,
)

# print("=== cache.py finished ===")
