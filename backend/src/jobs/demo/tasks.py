from core.celery_app import celery_app


@celery_app.task
def demo_task(x, y):
    """A simple demo task that adds two numbers."""
    z = x + y
    print("== Demo task executed - z = x + y ===")
    print(z)
    return z
