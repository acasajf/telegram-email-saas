import asyncio
import logging
import threading
from config import Config
from services.telegram_bot import TelegramBotService
from services.email_monitor import EmailMonitorService
from services.redis_subscriber import start_subscriber
from api.routes import app as flask_app

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)


def run_flask():
    """Roda Flask API em thread separada."""
    flask_app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=False,
        use_reloader=False,
    )


def run_email_monitor(telegram_bot):
    """Roda monitor de emails em thread separada."""
    monitor = EmailMonitorService(telegram_bot=telegram_bot)
    monitor.run()


async def main():
    """Entry point principal: inicia bot + email monitor + redis subscriber + API."""

    # Validar configuracoes
    Config.validate()

    logger.info("=" * 60)
    logger.info("SST FINDER - NOTIFICATION SERVICE")
    logger.info("=" * 60)
    logger.info(f"Ambiente: {Config.ENVIRONMENT}")

    # Iniciar Flask API em thread separada
    api_thread = threading.Thread(target=run_flask, daemon=True)
    api_thread.start()
    logger.info(f"Flask API rodando na porta {Config.API_PORT}")

    # Criar bot Telegram
    bot_service = TelegramBotService()

    # Iniciar monitor de emails em thread separada (se configurado)
    if Config.EMAIL_USER and Config.EMAIL_PASSWORD:
        email_thread = threading.Thread(
            target=run_email_monitor,
            args=(bot_service,),
            daemon=True,
        )
        email_thread.start()
        logger.info("Monitor de emails iniciado")
    else:
        logger.info("Monitor de emails desativado (IMAP nao configurado)")

    # Iniciar bot e subscriber Redis
    async with bot_service.app:
        await bot_service.app.start()
        await bot_service.app.updater.start_polling()
        logger.info("Telegram Bot iniciado")

        # Iniciar subscriber Redis (escuta eventos do sst-finder)
        logger.info("Iniciando Redis Subscriber...")
        try:
            await start_subscriber(bot_service.app.bot)
        except KeyboardInterrupt:
            logger.info("Encerrando...")
        finally:
            await bot_service.app.updater.stop()
            await bot_service.app.stop()


if __name__ == "__main__":
    asyncio.run(main())
