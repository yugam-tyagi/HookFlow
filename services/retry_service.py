def should_retry(attempt_count, response_status: int):
    if(200<= response_status < 300):
        return "delivered"

    if attempt_count >= 5:
        return "failed"
    delivery_status = None

    if response_status == 0:
        delivery_status = "retry"
    elif response_status in (408,429):
        delivery_status = "retry"
    elif 400 <= response_status < 500:
        delivery_status = "failed"         
    elif 500 <= response_status < 600:
        delivery_status = "retry"   
    else:
        delivery_status = "failed"

    return delivery_status


def calculate_retry_delay(attempt_count):
    if attempt_count == 1:
        return 5
    elif attempt_count == 2:
        return 15
    elif attempt_count == 3:
        return 45
    elif attempt_count == 4:
        return 120

    raise ValueError("Incorrect attempt count")