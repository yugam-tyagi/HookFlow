from celery_app import celery_app
from services import recovery_service

@celery_app.task(name="recover_deliveries")
def recover_deliveries():
    return recovery_service.recover_deliveries()