from celery_app import celery_app

@celery_app.task(name="process_delivery")
def process_delivery(delivery_id: str):
    return f"Received delivery with id: {delivery_id}"