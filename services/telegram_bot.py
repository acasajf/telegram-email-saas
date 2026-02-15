import uuid
import logging
import redis
import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from config.settings import TELEGRAM_BOT_TOKEN, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, SST_FINDER_URL

logger = logging.getLogger(__name__)

# Estados da conversa
WAITING_EMAIL = 0

# Cliente Redis para armazenar tokens
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /start - inicia processo de vinculação."""
    await update.message.reply_text(
        "Bem-vindo ao SST Finder Bot!\n\n"
        "Para receber notificações, preciso vincular sua conta.\n\n"
        "Por favor, digite o email cadastrado no SST Finder:"
    )
    return WAITING_EMAIL


async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe o email e tenta vincular a conta."""
    email = update.message.text.strip().lower()
    chat_id = update.effective_chat.id

    # Validação básica de email
    if "@" not in email or "." not in email:
        await update.message.reply_text(
            "Email inválido. Por favor, digite um email válido:"
        )
        return WAITING_EMAIL

    # Gerar token temporário e salvar no Redis (expira em 5 min)
    token = str(uuid.uuid4())
    redis_client.setex(f"telegram:link:{token}", 300, str(chat_id))

    # Chamar endpoint do sst-finder para vincular
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SST_FINDER_URL}/api/telegram/link",
                json={
                    "email": email,
                    "chatId": str(chat_id),
                    "token": token,
                },
                timeout=10,
            )

        if response.status_code == 200:
            await update.message.reply_text(
                "Conta vinculada com sucesso!\n\n"
                "Agora você receberá notificações do SST Finder "
                "diretamente aqui no Telegram.\n\n"
                "Comandos disponíveis:\n"
                "/status - Ver status da vinculação\n"
                "/parar - Desativar notificações\n"
                "/reativar - Reativar notificações"
            )
        elif response.status_code == 404:
            await update.message.reply_text(
                "Email não encontrado no SST Finder.\n"
                "Verifique se digitou corretamente ou cadastre-se em sstfinder.com"
            )
        else:
            data = response.json()
            error_msg = data.get("error", "Erro desconhecido")
            await update.message.reply_text(
                f"Erro ao vincular: {error_msg}\n"
                "Tente novamente com /start"
            )
    except httpx.TimeoutException:
        await update.message.reply_text(
            "O servidor SST Finder não respondeu a tempo.\n"
            "Tente novamente mais tarde com /start"
        )
    except Exception as e:
        logger.error(f"Erro ao vincular Telegram: {e}")
        await update.message.reply_text(
            "Erro interno. Tente novamente mais tarde com /start"
        )

    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela a conversa de vinculação."""
    await update.message.reply_text("Operação cancelada. Use /start para recomeçar.")
    return ConversationHandler.END


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica status da vinculação."""
    from database.connection import get_connection

    chat_id = str(update.effective_chat.id)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT name, email, "telegramNotifications" FROM users WHERE "telegramChatId" = %s',
                    (chat_id,),
                )
                user = cur.fetchone()

        if user:
            status = "ativas" if user["telegramNotifications"] else "desativadas"
            await update.message.reply_text(
                f"Conta vinculada:\n"
                f"Nome: {user['name']}\n"
                f"Email: {user['email']}\n"
                f"Notificações: {status}"
            )
        else:
            await update.message.reply_text(
                "Nenhuma conta vinculada.\nUse /start para vincular."
            )
    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")
        await update.message.reply_text("Erro ao verificar status. Tente novamente.")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Desativa notificações."""
    from database.connection import get_connection

    chat_id = str(update.effective_chat.id)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE users SET "telegramNotifications" = false WHERE "telegramChatId" = %s',
                    (chat_id,),
                )
                conn.commit()
                if cur.rowcount > 0:
                    await update.message.reply_text(
                        "Notificações desativadas.\n"
                        "Use /reativar para receber notificações novamente."
                    )
                else:
                    await update.message.reply_text(
                        "Nenhuma conta vinculada.\nUse /start para vincular."
                    )
    except Exception as e:
        logger.error(f"Erro ao desativar: {e}")
        await update.message.reply_text("Erro ao desativar. Tente novamente.")


async def reactivate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reativa notificações."""
    from database.connection import get_connection

    chat_id = str(update.effective_chat.id)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE users SET "telegramNotifications" = true WHERE "telegramChatId" = %s',
                    (chat_id,),
                )
                conn.commit()
                if cur.rowcount > 0:
                    await update.message.reply_text("Notificações reativadas com sucesso!")
                else:
                    await update.message.reply_text(
                        "Nenhuma conta vinculada.\nUse /start para vincular."
                    )
    except Exception as e:
        logger.error(f"Erro ao reativar: {e}")
        await update.message.reply_text("Erro ao reativar. Tente novamente.")


def create_bot_application() -> Application:
    """Cria e configura a aplicação do bot."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Conversa de vinculação
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            WAITING_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancel_command)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("parar", stop_command))
    app.add_handler(CommandHandler("reativar", reactivate_command))

    return app
