from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from services.control_api.src.control_api.domain.schemas import EvaluateResponse
from services.data_plane.src.data_plane.core.db import get_db_session
from services.data_plane.src.data_plane.services.evaluator import evaluate

router = APIRouter(prefix="/v1")


@router.get("/evaluate", response_model=EvaluateResponse)
async def evaluate_flags(
    env: str, user_id: str, db: AsyncSession = Depends(get_db_session)
) -> EvaluateResponse:
    try:
        flags = await evaluate(env=env, user_id=user_id, db=db)
    except ValueError as e:
        if str(e) == "environment_not_found":
            raise HTTPException(status_code=404, detail="environment not found") from e
        raise

    return EvaluateResponse(env=env, user_id=user_id, flags=flags)
