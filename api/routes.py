from fastapi import FastAPI
from database.connection import get_connection

app = FastAPI(title="SST Finder - Telegram Notification Service")


@app.get("/health")
async def health_check():
    """Health check do serviço."""
    checks = {"api": True, "database": False, "redis": False}

    # Check DB
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        checks["database"] = True
    except Exception:
        pass

    # Check Redis
    try:
        import redis
        from config.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
        r.ping()
        checks["redis"] = True
    except Exception:
        pass

    healthy = all(checks.values())
    return {"status": "healthy" if healthy else "degraded", "checks": checks}


@app.get("/stats")
async def stats():
    """Estatísticas do serviço de notificações."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT COUNT(*) as total FROM users WHERE "telegramChatId" IS NOT NULL'
                )
                result = cur.fetchone()
                linked_users = result["total"] if result else 0

                cur.execute(
                    'SELECT COUNT(*) as total FROM users WHERE "telegramNotifications" = true'
                )
                result = cur.fetchone()
                active_notifications = result["total"] if result else 0

        return {
            "linked_users": linked_users,
            "active_notifications": active_notifications,
        }
    except Exception as e:
        return {"error": str(e)}
