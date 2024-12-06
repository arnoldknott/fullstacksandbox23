import redis

from core.config import config

# print("=== cache.py started ===")

redis_session_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD,
    db=config.REDIS_SESSION_DB,
)

# print("=== cache.py finished ===")
