from core.config import config

broker = f"redis://socketio:{config.REDIS_WORKER_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_WORKER_DB}"
