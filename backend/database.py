"""MongoDB + Redis connection managers."""
import redis.asyncio as aioredis
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import get_settings

settings = get_settings()

# ── MongoDB ──────────────────────────────────────────────────────────────────
_mongo_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
    return _mongo_client


def get_db():
    return get_mongo_client()[settings.MONGODB_DB]


# ── Redis ─────────────────────────────────────────────────────────────────────
_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        url = settings.REDIS_URL
        if url.startswith("rediss://"):
            _redis_client = aioredis.from_url(
                url,
                decode_responses=True,
                ssl_cert_reqs=None,
            )
        else:
            _redis_client = aioredis.from_url(url, decode_responses=True)
    return _redis_client


async def get_or_cache(key: str, ttl: int, generator):
    """Generic Redis cache helper. generator is an async callable."""
    redis = await get_redis()
    cached = await redis.get(key)
    if cached:
        return cached
    result = await generator()
    await redis.setex(key, ttl, result)
    return result


# ── Indexes (run once on startup) ────────────────────────────────────────────
async def ensure_indexes():
    db = get_db()
    await db.videos.create_index("video_id", unique=True)
    await db.user_videos.create_index([("user_id", 1), ("created_at", -1)])
    await db.jobs.create_index("job_id", unique=True)
    await db.jobs.create_index("created_at", expireAfterSeconds=86400)  # TTL 24h
    await db.chat_sessions.create_index([("user_id", 1), ("video_id", 1)])
