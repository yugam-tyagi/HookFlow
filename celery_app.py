import os
from celery import Celery

BROKER_URL = os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "hookflow",
    broker=BROKER_URL,
    include=["tasks.delivery_tasks","tasks.recovery_tasks"]
)

celery_app.conf.update(
    task_ignore_result=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_transport_options={
        "visibility_timeout": 300
    },
    beat_schedule={
        "recover-pending-deliveries":{
            "task": "recover_deliveries",
            "schedule": 30.0
        }
    }
)