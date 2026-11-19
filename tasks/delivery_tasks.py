from celery_app import celery_app

@celery_app.task(name="test_task")
def test_task(name):
    return f"Swadeka {name}. Do you want thai tea?"