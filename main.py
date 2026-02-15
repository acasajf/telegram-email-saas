import asyncio
import logging
import threading
import uvicorn
from config.settings import TELEGRAM_BOT_TOKEN, API_PORT
from services.telegram_bot import create_bot_application
from services.redis_subscriber import start_subscriber
from api.routes import app as fastapi_app

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def run_fastapi():
    """Roda FastAPI em thread separada."""
    uvicorn.run(fastapi_app, host="0.0.0.0", port=API_PORT, log_level="info")


async def main():
    """Entry point principal: inicia bot + subscriber + API."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN não configurado. Verifique o .env")
        return

    logger.info("=" * 60)
    logger.info("SST FINDER - TELEGRAM NOTIFICATION SERVICE")
    logger.info("=" * 60)

    # Iniciar FastAPI em thread separada
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()
    logger.info(f"FastAPI rodando na porta {API_PORT}")

    # Criar aplicação do bot
    bot_app = create_bot_application()

    # Iniciar bot e subscriber
    async with bot_app:
        await bot_app.start()
        await bot_app.updater.start_polling()
        logger.info("Telegram Bot iniciado")

        # Iniciar subscriber Redis (roda indefinidamente)
        logger.info("Iniciando Redis Subscriber...")
        try:
            await start_subscriber(bot_app)
        except KeyboardInterrupt:
            logger.info("Encerrando...")
        finally:
            await bot_app.updater.stop()
            await bot_app.stop()


if __name__ == "__main__":
    asyncio.run(main())
