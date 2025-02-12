from sqlalchemy_service import BaseService as BaseRepository
from uuid import UUID

from app.db.tables import TaskImage


class TaskImageRepository[Table: TaskImage, int](BaseRepository):
    base_table = TaskImage

    async def create(self, model: TaskImage) -> TaskImage:
        self.session.add(model)
        await self._commit()
        self.response.status_code = 201
        return await self.get(model.id)

    async def list(self, page=None, count=None) -> list[TaskImage]:
        return list(await self._get_list(page=page, count=count))

    async def get(self, model_id: UUID) -> TaskImage:
        return await self._get_one(
            id=model_id,
        )

    async def update(self, model_id: UUID, **fields) -> TaskImage:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: UUID):
        await self._delete(model_id)

