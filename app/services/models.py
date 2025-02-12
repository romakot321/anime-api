from fastapi import Depends

from app.repositories.prompt import PromptRepository
from app.schemas.models import ModelSearchSchema, ModelSchema


class ModelsService:
    def __init__(
            self,
            prompt_repository: PromptRepository = Depends()
    ):
        self.prompt_repository = prompt_repository

    async def list(self, schema: ModelSearchSchema) -> list[ModelSchema]:
        prompts = await self.prompt_repository.list(is_model=True, **schema.model_dump())
        return [
            ModelSchema.model_validate(prompt)
            for prompt in prompts
        ]

