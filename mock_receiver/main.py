import asyncio
from fastapi import FastAPI, status, Response

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