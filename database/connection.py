import psycopg2
from psycopg2.extras import RealDictCursor
from config.settings import DATABASE_URL


def get_connection():
    """Cria conexão com o PostgreSQL do sst-finder."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def get_user_by_id(user_id: str) -> dict | None:
    """Busca usuário pelo ID e retorna dados com telegram_chat_id."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, email, role, "telegramChatId", "telegramNotifications"
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )
            return cur.fetchone()


def get_user_by_email(email: str) -> dict | None:
    """Busca usuário pelo email."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, email, role, "telegramChatId", "telegramNotifications"
                FROM users
                WHERE email = %s
                """,
                (email.lower(),),
            )
            return cur.fetchone()


def get_admin_users() -> list[dict]:
    """Busca todos os admins com Telegram vinculado."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, email, "telegramChatId"
                FROM users
                WHERE role IN ('SUPER_ADMIN', 'ADMIN')
                  AND "telegramChatId" IS NOT NULL
                  AND "telegramNotifications" = true
                """,
            )
            return cur.fetchall()
