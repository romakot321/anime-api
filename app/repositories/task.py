from sqlalchemy_service import BaseService as BaseRepository
from sqlalchemy import select
from uuid import UUID

from app.db.tables import Task, TaskItem, TaskStatus


class TaskRepository[Table: Task, int](BaseRepository):
    base_table = Task

    async def create(self, model: Task) -> Task:
        self.session.add(model)
        await self._commit()
        self.response.status_code = 201
        return await self.get(model.id)

    async def create_items(self, *models: TaskItem):
        [self.session.add(model) for model in models]
        await self._commit()

    async def list_queued(self) -> list[Task]:
        query = self._select_in_load_query([Task.items])
        query = query.filter(Task.items.any(TaskItem.status == TaskStatus.queued))
        return list(await self.session.scalars(query))

    async def list(self, page=None, count=None) -> list[Task]:
        return list(await self._get_list(page=page, count=count))

    async def get(self, model_id: UUID) -> Task:
        return await self._get_one(
            id=model_id,
            select_in_load=[Task.items, Task.images]
        )

    async def update(self, model_id: UUID, **fields) -> Task:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: UUID):
        await self._delete(model_id)

