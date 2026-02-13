from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.control_api.src.control_api.db import get_db_session
from services.control_api.src.control_api.evaluate import is_in_rollout
from services.control_api.src.control_api.models import Environment, FeatureFlag, FeatureFlagState
from services.control_api.src.control_api.schemas import (
    EnvCreate,
    EnvOut,
    EvaluateResponse,
    FlagCreate,
    FlagOut,
    FlagStateUpsert,
)

router = APIRouter(prefix="/v1")


@router.post("/envs", response_model=EnvOut)
async def create_env(payload: EnvCreate, db: AsyncSession = Depends(get_db_session)) -> EnvOut:
    existing = await db.scalar(select(Environment).where(Environment.name == payload.name))
    if existing is not None:
        raise HTTPException(status_code=409, detail="environment already exists")
    env = Environment(name=payload.name)
    db.add(env)
    await db.commit()
    await db.refresh(env)
    return env


@router.get("/envs", response_model=list[EnvOut])
async def list_envs(db: AsyncSession = Depends(get_db_session)) -> list[EnvOut]:
    rows = (await db.scalars(select(Environment).order_by(Environment.id))).all()
    return list(rows)


@router.post("/flags", response_model=FlagOut)
async def create_flag(payload: FlagCreate, db: AsyncSession = Depends(get_db_session)) -> FlagOut:
    existing = await db.scalar(select(FeatureFlag).where(FeatureFlag.key == payload.key))
    if existing is not None:
        raise HTTPException(status_code=409, detail="flag already exists")
    flag = FeatureFlag(key=payload.key, description=payload.description)
    db.add(flag)
    await db.commit()
    await db.refresh(flag)
    return flag


@router.get("/flags", response_model=list[FlagOut])
async def list_flags(db: AsyncSession = Depends(get_db_session)) -> list[FlagOut]:
    rows = (await db.scalars(select(FeatureFlag).order_by(FeatureFlag.id))).all()
    return list(rows)


@router.put("/flags/{flag_key}/state/{env_name}")
async def upsert_flag_state(
    flag_key: str,
    env_name: str,
    payload: FlagStateUpsert,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    flag = await db.scalar(select(FeatureFlag).where(FeatureFlag.key == flag_key))
    if flag is None:
        raise HTTPException(status_code=404, detail="flag not found")

    env = await db.scalar(select(Environment).where(Environment.name == env_name))
    if env is None:
        raise HTTPException(status_code=404, detail="environment not found")

    state = await db.scalar(
        select(FeatureFlagState).where(
            FeatureFlagState.flag_id == flag.id,
            FeatureFlagState.environment_id == env.id,
        )
    )

    if state is None:
        state = FeatureFlagState(
            flag_id=flag.id,
            environment_id=env.id,
            enabled=payload.enabled,
            rollout_percentage=payload.rollout_percentage,
        )
        db.add(state)
    else:
        state.enabled = payload.enabled
        state.rollout_percentage = payload.rollout_percentage

    await db.commit()
    return {"status": "ok"}


@router.get("/evaluate", response_model=EvaluateResponse)
async def evaluate_flags(
    env: str, user_id: str, db: AsyncSession = Depends(get_db_session)
) -> EvaluateResponse:
    env_obj = await db.scalar(select(Environment).where(Environment.name == env))
    if env_obj is None:
        raise HTTPException(status_code=404, detail="environment not found")

    stmt = (
        select(FeatureFlag.key, FeatureFlagState.enabled, FeatureFlagState.rollout_percentage)
        .join(FeatureFlagState, FeatureFlagState.flag_id == FeatureFlag.id)
        .where(FeatureFlagState.environment_id == env_obj.id)
    )
    rows = (await db.execute(stmt)).all()

    result: dict[str, bool] = {}
    for flag_key, enabled, pct in rows:
        if not enabled:
            result[flag_key] = False
        else:
            result[flag_key] = is_in_rollout(
                flag_key=flag_key, env=env, user_id=user_id, rollout_percentage=pct
            )

    return EvaluateResponse(env=env, user_id=user_id, flags=result)
