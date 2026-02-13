from redis.asyncio import Redis

from services.data_plane.src.data_plane.core.config import settings

redis_client: Redis = Redis.from_url(settings.redis_url, decode_responses=True)
