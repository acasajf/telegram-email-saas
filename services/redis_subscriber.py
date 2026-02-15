import json
import asyncio
import logging
import redis
from telegram.ext import Application
from config.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, NOTIFICATION_CHANNEL
from services.notification_handler import format_message, get_recipients

logger = logging.getLogger(__name__)


async def start_subscriber(bot_app: Application):
    """Inicia o subscriber Redis que escuta notificações do sst-finder."""
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )

    pubsub = redis_client.pubsub()
    pubsub.subscribe(NOTIFICATION_CHANNEL)

    logger.info(f"[SUBSCRIBER] Escutando canal '{NOTIFICATION_CHANNEL}'...")

    bot = bot_app.bot

    while True:
        try:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

            if message and message["type"] == "message":
                try:
                    payload = json.loads(message["data"])
                    event = payload.get("event", "")
                    data = payload.get("data", {})
                    user_id = payload.get("userId")

                    logger.info(f"[SUBSCRIBER] Evento recebido: {event}")

                    # Buscar destinatários
                    chat_ids = get_recipients(event, data, user_id)

                    if not chat_ids:
                        logger.debug(f"[SUBSCRIBER] Nenhum destinatário para {event}")
                        continue

                    # Formatar mensagem
                    text = format_message(event, data)

                    # Enviar para todos os destinatários
                    for chat_id in chat_ids:
                        try:
                            await bot.send_message(
                                chat_id=chat_id,
                                text=text,
                                parse_mode="HTML",
                            )
                            logger.info(f"[SUBSCRIBER] Notificação enviada para {chat_id}")
                        except Exception as e:
                            logger.error(f"[SUBSCRIBER] Erro ao enviar para {chat_id}: {e}")

                except json.JSONDecodeError:
                    logger.error("[SUBSCRIBER] Payload inválido (não é JSON)")
                except Exception as e:
                    logger.error(f"[SUBSCRIBER] Erro ao processar evento: {e}")

            await asyncio.sleep(0.1)

        except redis.ConnectionError:
            logger.error("[SUBSCRIBER] Conexão Redis perdida. Reconectando em 5s...")
            await asyncio.sleep(5)
            try:
                pubsub = redis_client.pubsub()
                pubsub.subscribe(NOTIFICATION_CHANNEL)
                logger.info("[SUBSCRIBER] Reconectado ao Redis")
            except Exception:
                pass
        except Exception as e:
            logger.error(f"[SUBSCRIBER] Erro inesperado: {e}")
            await asyncio.sleep(1)
