from fastapi import APIRouter, Depends

from app.routes import validate_api_token
from app.schemas.models import ModelSearchSchema, ModelSchema
from app.services.models import ModelsService

router = APIRouter(prefix="/api/models", tags=["Models"])


@router.get(
    "",
    response_model=list[ModelSchema],
    dependencies=[Depends(validate_api_token)]
)
async def list_models(
        schema: ModelSearchSchema = Depends(),
        service: ModelsService = Depends()
):
    return await service.list(schema)

