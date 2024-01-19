import redis
from core.config import config

# print("=== cache.py started ===")

# print("=== config.REDIS_HOST ===")
# print(config.REDIS_HOST)
# print("=== config.REDIS_PORT ===")
# print(config.REDIS_PORT)
# print("=== config.REDIS_JWKS_DB ===")
# print(config.REDIS_JWKS_DB)

redis_jwks_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD,
    db=config.REDIS_JWKS_DB,
)

# print("=== cache.py finished ===")
