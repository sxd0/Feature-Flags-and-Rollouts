from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from libs.common.src.common.flags.rollout import is_in_rollout
from services.control_api.src.control_api.domain.models import Environment, FeatureFlag, FeatureFlagState

async def evaluate(env: str, user_id: str, db: AsyncSession) -> dict[str, bool]:
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
            result[flag_key] = is_in_rollout(flag_key=flag_key, env=env, user_id=user_id, rollout_percentage=pct)

    return result
