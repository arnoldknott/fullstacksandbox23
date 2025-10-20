from celery import Celery

from core.celeryconfig import celeryconfig

celery_app = Celery("backend_jobs", **celeryconfig)
print("👍 ⛏️ Celery started")
