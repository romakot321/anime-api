import io
from typing import BinaryIO
from uuid import UUID
from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy_service.base_db.base import asyncio
from loguru import logger

from app.repositories.external import ExternalRepository
from app.repositories.prompt import PromptRepository
from app.repositories.task import TaskRepository
from app.repositories.task_image import TaskImageRepository
from app.repositories.task_item import TaskItemRepository
from app.schemas.external import ExternalVideoGeneration
from app.schemas.task import TaskImageCreateSchema, TaskSchema, TaskVideoCreateSchema
from app.db.tables import Task, TaskImage, TaskItem, TaskStatus, TaskType


class TaskService:
    def __init__(
            self,
            task_repository: TaskRepository = Depends(),
            task_item_repository: TaskItemRepository = Depends(),
            image_repository: TaskImageRepository = Depends(),
            external_repository: ExternalRepository = Depends(),
            prompt_repository: PromptRepository = Depends()
    ):
        self.task_repository = task_repository
        self.external_repository = external_repository
        self.prompt_repository = prompt_repository
        self.task_item_repository = task_item_repository
        self.image_repository = image_repository

    async def _save_image(self, image_buffer: BinaryIO, task_id: UUID):
        external_id = await self.external_repository.upload_image_for_video(image_buffer)
        model = TaskImage(task_id=task_id, external_id=external_id)
        await self.image_repository.create(model)

    async def get(self, task_id: UUID) -> TaskSchema:
        model = await self.task_repository.get(task_id)
        return TaskSchema(
            id=model.id,
            error=model.error,
            status=model.items[0].status,
            result_url=(model.items[0].result_url if model.items[0].status == TaskStatus.finished else None)
        )

    async def create_video(self, schema: TaskVideoCreateSchema, file: UploadFile) -> TaskSchema:
        model = Task(app_bundle=schema.app_bundle, user_id=schema.user_id, type=TaskType.video)
        model = await self.task_repository.create(model)
        await self._save_image(file.file, model.id)
        return TaskSchema.model_validate(model)

    async def create_image(self, schema: TaskImageCreateSchema) -> TaskSchema:
        model = Task(app_bundle=schema.app_bundle, user_id=schema.user_id, type=TaskType.image)
        model = await self.task_repository.create(model)
        return TaskSchema.model_validate(model)

    async def start_video(self, task_id: UUID, schema: TaskVideoCreateSchema):
        task = await self.task_repository.get(task_id)
        if not task.images:
            raise ValueError("Task hasn't image")

        if schema.model_id is not None:
            prompt = await self.prompt_repository.get(schema.model_id)
        else:
            prompt = await self.prompt_repository.get_video_basic()

        external_id = await self.external_repository.start_video_generate(prompt.text, task.images[0].external_id)
        await self.task_repository.create_items(
            TaskItem(task_id=task_id, external_id=external_id, result_url=self.external_repository.make_video_url(external_id))
        )

    async def start_image_to_image(self, task_id: UUID, image_body: bytes, schema: TaskImageCreateSchema):
        task = await self.task_repository.get(task_id)

        if schema.model_id is not None:
            prompt_model = await self.prompt_repository.get(schema.model_id)
        else:
            prompt_model = await self.prompt_repository.get_image_basic()
        prompt_text = prompt_model.text + schema.prompt
        image = io.BytesIO(image_body)
        image.name = "a.jpg"

        external_id = await self.external_repository.start_image2image_generate(prompt_text, image, schema.aspect_ratio.value)
        await self.task_repository.create_items(
            TaskItem(task_id=task_id, external_id=external_id, result_url=None)
        )

    async def start_image(self, task_id: UUID, schema: TaskImageCreateSchema):
        task = await self.task_repository.get(task_id)

        if schema.model_id is not None:
            prompt_model = await self.prompt_repository.get(schema.model_id)
        else:
            prompt_model = await self.prompt_repository.get_image_basic()
        prompt_text = prompt_model.text + schema.prompt

        external_id = await self.external_repository.start_image_generate(prompt_text, schema.aspect_ratio.value)
        await self.task_repository.create_items(
            TaskItem(task_id=task_id, external_id=external_id, result_url=None)
        )

    async def _get_video_status(self, external_id: str) -> TaskStatus:
        response = await self.external_repository.get_video_generation(external_id)
        if response.is_finished:
            return TaskStatus.finished
        if response.is_invalid:
            return TaskStatus.error
        return TaskStatus.queued

    async def _update_video_status(self, task: Task):
        if not task.items:
            raise ValueError("Task hasn't items")
        status = await self._get_video_status(str(task.items[0].external_id))
        if status == TaskStatus.queued:
            return
        await self.task_item_repository.update(task.items[0].id, status=status)

    async def _update_image_status(self, task: Task):
        if not task.items:
            raise ValueError("Task hasn't items")
        response = await self.external_repository.get_image_generation(str(task.items[0].external_id))
        if not response.is_finished and not response.is_invalid:
            return
        elif response.is_invalid:
            await self.task_item_repository.update(task.items[0].id, status=TaskStatus.error)
        else:
            await self.task_item_repository.update(task.items[0].id, status=TaskStatus.finished, result_url=response.image_url)

    @classmethod
    async def update_tasks(cls):
        async with cls() as self:
            tasks = await self.task_repository.list_queued()
            await asyncio.gather(*[
                (self._update_video_status(task) if task.type == TaskType.video else self._update_image_status(task))
                for task in tasks
            ])

    async def __aenter__(self):
        self.task_repository = TaskRepository()
        await self.task_repository.__aenter__()
        self.image_repository = TaskImageRepository(session=self.task_repository.session)
        self.external_repository = ExternalRepository()
        self.prompt_repository = PromptRepository(session=self.task_repository.session)
        self.task_item_repository = TaskItemRepository(session=self.task_repository.session)
        return self

    async def __aexit__(self, *exc_info):
        await self.task_repository.__aexit__()
        return self

