import asyncio, os, hmac, hashlib
from fastapi import FastAPI, status, Response, Request
from fastapi.responses import JSONResponse


app = FastAPI(
    title="Mock Receiver",
    description="Mock reciever to test Hookflow",
    version="1.0.0",
)


@app.post("/webhooks/success")
def webhook_success():
    return Response(content="Order event accepted successfully",status_code=status.HTTP_200_OK)


@app.post("/webhooks/bad-request")
def webhook_bad_request():
    return Response(content="Invalid webhook payload",status_code=status.HTTP_400_BAD_REQUEST)


@app.post("/webhooks/failure")
def webhook_failure():
    return Response(content="Internal server error at receiver",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/webhooks/timeout")
async def webhook_timeout():
    await asyncio.sleep(15)
    return Response(content="Receiver response delayed",status_code=status.HTTP_408_REQUEST_TIMEOUT)


@app.post("/webhooks/permanent-failure")
def webhook_permanent_failure():
    return Response(content="Invalid webhook request - permanent failure", status_code=status.HTTP_400_BAD_REQUEST)


fail_four_times_attempts = 0
@app.post("/webhooks/fail-four-times")
def webhook_fail_four_times():
    global fail_four_times_attempts
    fail_four_times_attempts += 1

    if fail_four_times_attempts <= 4:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Simulated temporary receiver failure",
                "attempt": fail_four_times_attempts
            }
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Webhook received successfully",
            "attempt": fail_four_times_attempts
        }
    )


@app.post("/webhooks/verify")
async def verify_webhook(request: Request):
    body = await request.body()

    timestamp = request.headers.get("X-HookFlow-Timestamp")
    received_signature = request.headers.get("X-HookFlow-Signature")

    if not timestamp or not received_signature:
        return JSONResponse(status_code=400,content={"message": "Missing signature headers"})

    signing_secret = os.getenv("HOOKFLOW_SIGNING_SECRET")
    message = timestamp.encode("utf-8") + b"." + body

    expected_signature = hmac.new(key=signing_secret.encode("utf-8"),msg=message,digestmod=hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, received_signature):
        return JSONResponse(status_code=401,content={"message": "Invalid signature"})

    return JSONResponse(status_code=200,content={"message": "Signature verified successfully"})