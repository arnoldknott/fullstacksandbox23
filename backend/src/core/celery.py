from core.config import config
from celery import Celery

print("👍 ⛏️ Celery started")

broker = f"redis://worker:{config.REDIS_WORKER_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_WORKER_DB}"

celery_app = Celery("tasks", broker=broker)
