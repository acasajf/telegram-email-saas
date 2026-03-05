import json
import asyncio
import logging
import redis
from config import Config
from services.notification_handler import format_message, get_recipients

logger = logging.getLogger(__name__)


async def start_subscriber(bot):
    """Inicia o subscriber Redis que escuta notificacoes do sst-finder."""
    try:
        redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD,
            decode_responses=True,
        )

        # Testar conexão
        redis_client.ping()

        pubsub = redis_client.pubsub()
        pubsub.subscribe(Config.NOTIFICATION_CHANNEL)

        logger.info(f"[SUBSCRIBER] Escutando canal '{Config.NOTIFICATION_CHANNEL}'...")
    except (redis.ConnectionError, Exception) as e:
        logger.warning(f"[SUBSCRIBER] Redis nao disponivel: {e}")
        logger.info("[SUBSCRIBER] Servico continuara sem Redis (sem integracao SST Finder)")
        # Manter o loop rodando mas sem fazer nada
        while True:
            await asyncio.sleep(60)
        return

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

                    # Buscar destinatarios
                    chat_ids = get_recipients(event, data, user_id)

                    if not chat_ids:
                        logger.debug(f"[SUBSCRIBER] Nenhum destinatario para {event}")
                        continue

                    # Formatar mensagem
                    text = format_message(event, data)

                    # Enviar para todos os destinatarios
                    for chat_id in chat_ids:
                        try:
                            await bot.send_message(
                                chat_id=chat_id,
                                text=text,
                                parse_mode="HTML",
                            )
                            logger.info(f"[SUBSCRIBER] Notificacao enviada para {chat_id}")
                        except Exception as e:
                            logger.error(f"[SUBSCRIBER] Erro ao enviar para {chat_id}: {e}")

                except json.JSONDecodeError:
                    logger.error("[SUBSCRIBER] Payload invalido (nao e JSON)")
                except Exception as e:
                    logger.error(f"[SUBSCRIBER] Erro ao processar evento: {e}")

            await asyncio.sleep(0.1)

        except redis.ConnectionError:
            logger.error("[SUBSCRIBER] Conexao Redis perdida. Reconectando em 5s...")
            await asyncio.sleep(5)
            try:
                pubsub = redis_client.pubsub()
                pubsub.subscribe(Config.NOTIFICATION_CHANNEL)
                logger.info("[SUBSCRIBER] Reconectado ao Redis")
            except Exception:
                pass
        except Exception as e:
            logger.error(f"[SUBSCRIBER] Erro inesperado: {e}")
            await asyncio.sleep(1)
