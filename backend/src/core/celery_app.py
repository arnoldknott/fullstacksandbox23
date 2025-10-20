from celery import Celery
from core.celeryconfig import celeryconfig

celery_app = Celery("worker", **celeryconfig)
print("👍 ⛏️ Celery started")
