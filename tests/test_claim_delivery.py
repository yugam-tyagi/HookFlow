import pytest
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from repositories import delivery_repository
from database import deliveries_collection


@pytest.mark.parametrize(
    "initial_status, next_attempt_offset, lease_offset, expected_claim",
    [
        ("pending", -10, None, True),
        ("retrying", -10, None, True),
        ("pending", 10, None, False),
        ("retrying", 10, None, False),
        ("processing", None, -10, True),
        ("processing", None, 10, False),
    ]
)
def test_claim_delivery(initial_status,next_attempt_offset,lease_offset,expected_claim):
    now = datetime.now(timezone.utc)
    delivery_id = ObjectId()

    delivery = {
        "_id": delivery_id,
        "status": initial_status,
        "attempt_count": 0
    }

    if next_attempt_offset is not None:
        delivery["next_attempt_at"] = now + timedelta(seconds=next_attempt_offset)

    if lease_offset is not None:
        delivery["lease_expires_at"] = now + timedelta(seconds=lease_offset)

    deliveries_collection.insert_one(delivery)

    claimed_delivery = delivery_repository.claim_delivery(str(delivery_id))

    if expected_claim:
        assert claimed_delivery is not None
        assert claimed_delivery["status"] == "processing"
        assert claimed_delivery["processing_started_at"] is not None
        assert claimed_delivery["lease_expires_at"] > now
    else:
        assert claimed_delivery is None


def test_claim_delivery_prevents_duplicate_claim():
    delivery_id = ObjectId()
    now = datetime.now(timezone.utc)

    deliveries_collection.insert_one({
        "_id": delivery_id,
        "status": "pending",
        "next_attempt_at": now - timedelta(seconds=10),
        "attempt_count": 0
    })

    first_claim = delivery_repository.claim_delivery(str(delivery_id))
    second_claim = delivery_repository.claim_delivery(str(delivery_id))

    assert first_claim is not None
    assert first_claim["status"] == "processing"
    assert second_claim is None


def test_claim_delivery_reclaims_expired_lease():
    delivery_id = ObjectId()
    now = datetime.now(timezone.utc)

    deliveries_collection.insert_one({
        "_id": delivery_id,
        "status": "processing",
        "processing_started_at": now - timedelta(seconds=120),
        "lease_expires_at": now - timedelta(seconds=60),
        "attempt_count": 1
    })

    claimed_delivery = delivery_repository.claim_delivery(str(delivery_id))

    assert claimed_delivery is not None
    assert claimed_delivery["status"] == "processing"
    assert claimed_delivery["processing_started_at"] > now - timedelta(seconds=5)
    assert claimed_delivery["lease_expires_at"] > now