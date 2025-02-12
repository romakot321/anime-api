from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile, File

from app.routes import validate_api_token
from app.services.task import TaskService
from app.schemas.task import TaskVideoCreateSchema, TaskImageCreateSchema, TaskSchema

router = APIRouter(prefix="/api/task", tags=["Animate task"])


@router.post(
    "/image",
    response_model=TaskSchema,
    dependencies=[Depends(validate_api_token)],
    description="Создание задачи на генерацию аниме-изображения, исходя из предпочтений пользователя(prompt). model_id - необязательное, брать из списка моделей"
)
async def generate_image(
        schema: TaskImageCreateSchema,
        background_tasks: BackgroundTasks,
        service: TaskService = Depends()
):
    model = await service.create_image(schema)
    background_tasks.add_task(service.start_image, model.id, schema)
    return model


@router.post(
    "/video",
    response_model=TaskSchema,
    dependencies=[Depends(validate_api_token)],
    description="Создание задачи на генерацию видео. model_id - необязательное, брать из списка моделей"
)
async def generate_video(
        schema: TaskVideoCreateSchema,
        background_tasks: BackgroundTasks,
        file: UploadFile = File(),
        service: TaskService = Depends()
):
    model = await service.create_video(schema, file)
    background_tasks.add_task(service.start_video, model.id, schema)
    return model


@router.get(
    "/{task_id}",
    response_model=TaskSchema,
    dependencies=[Depends(validate_api_token)],
    description="Получение статуса и ссылки на результат генерации"
)
async def get_task_status(
        task_id: UUID,
        service: TaskService = Depends()
):
    return await service.get(task_id)

