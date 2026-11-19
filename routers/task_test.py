from fastapi import APIRouter,status
from schemas.test_task import TestTaskCreate, TestTaskResponse
from tasks.delivery_tasks import test_task as celery_test_task

router = APIRouter(prefix="/test-task",tags=["test-task"])

@router.post("/",response_model=TestTaskResponse,status_code=status.HTTP_202_ACCEPTED)
def test_task(request: TestTaskCreate):
    name = request.name
    result = celery_test_task.delay(name)
    return TestTaskResponse(
        message="Task submitted successfully",
        task_id=result.id
    )