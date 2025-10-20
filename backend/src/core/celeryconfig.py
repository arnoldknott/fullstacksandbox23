from core.config import config

celeryconfig = {
    "broker": f"redis://celery:{config.REDIS_CELERY_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_CELERY_BROKER_DB}",
    "backend": f"redis://celery:{config.REDIS_CELERY_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_CELERY_BACKEND_DB}",
    # Add other modules manually here:
    "include": ["jobs.demo.tasks"],
}
