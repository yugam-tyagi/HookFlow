import pytest
from services import retry_service

@pytest.mark.parametrize(
    "attempt_count, status_code, expected_result",
    [
        (1,200,"delivered"),
        (5,201,"delivered"),
        (1,400,"failed"),
        (1,408,"retry"),
        (1,429,"retry"),
        (1,500,"retry"),
        (1,0,"retry"),
        (5,500,"failed"),
        (5,0,"failed")
    ]
)
def test_should_retry(attempt_count, status_code, expected_result):
    assert retry_service.should_retry(attempt_count, status_code) == expected_result


@pytest.mark.parametrize(
    "attempt_count, expected_result",
    [
        (1,5),
        (2,15),
        (3,45),
        (4,120)
    ]
)
def test_calculate_retry_delay(attempt_count, expected_result):
    assert retry_service.calculate_retry_delay(attempt_count) == expected_result


@pytest.mark.parametrize(
    "attempt_count",
    [
        (5),
        (0),
        (-1)
    ]
)
def test_calculate_retry_delay_invalid_attempt(attempt_count):
    with pytest.raises(ValueError):
        retry_service.calculate_retry_delay(attempt_count)