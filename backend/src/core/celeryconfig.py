from core.config import config

celeryconfig = {
    "broker": f"redis://worker:{config.REDIS_WORKER_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_WORKER_DB}"
    # TBD: add backend
}

