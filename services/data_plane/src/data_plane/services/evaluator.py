import json
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from libs.common.src.common.flags.rollout import is_in_rollout
from services.control_api.src.control_api.domain.models import (
    Environment,
    FeatureFlag,
    FeatureFlagState,
)
from services.data_plane.src.data_plane.core.config import settings
from services.data_plane.src.data_plane.core.redis import redis_client


def _cache_key(env: str, user_id: str) -> str:
    return f"eval:{env}:{user_id}"


async def evaluate(env: str, user_id: str, db: AsyncSession) -> dict[str, bool]:
    key = _cache_key(env, user_id)
    cached = await redis_client.get(key)
    if cached is not None:
        return cast(dict[str, bool], json.loads(cached))

    env_obj = await db.scalar(select(Environment).where(Environment.name == env))
    if env_obj is None:
        raise ValueError("environment_not_found")

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

    await redis_client.set(key, json.dumps(result), ex=settings.cache_ttl_seconds)
    return result
