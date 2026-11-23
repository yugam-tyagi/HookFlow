from datetime import datetime, timezone
from repositories import delivery_repository
from tasks import delivery_tasks

def recover_deliveries():
    current_timestamp = datetime.now(timezone.utc)
    delivery_ids = delivery_repository.get_deliveries_for_recovery(current_timestamp)
    deliveries_enqueued = 0

    for id in delivery_ids:
        delivery_tasks.process_delivery.delay(str(id))
        deliveries_enqueued += 1

    return deliveries_enqueued