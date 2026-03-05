import imaplib
import email
from email.header import decode_header
from config import Config
import time
import asyncio
import logging

logger = logging.getLogger(__name__)


class EmailMonitorService:
    def __init__(self, telegram_bot=None):
        self._db = None
        self.telegram = telegram_bot
        self.imap = None

    @property
    def db(self):
        """Lazy-load do database (opcional)."""
        if self._db is None:
            try:
                from database import SupabaseDB
                self._db = SupabaseDB()
                logger.info("Supabase conectado no Email Monitor")
            except Exception as e:
                logger.warning(f"Supabase nao disponivel no Email Monitor: {e}")
                self._db = False
        return self._db if self._db is not False else None

    def connect(self):
        """Conecta ao servidor IMAP"""
        try:
            self.imap = imaplib.IMAP4_SSL(Config.IMAP_SERVER, Config.IMAP_PORT)
            self.imap.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            logger.info(f"Conectado ao email: {Config.EMAIL_USER}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao email: {e}")
            return False

    def decode_header_value(self, header_value):
        """Decodifica header do email"""
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        result = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                result += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                result += str(part)

        return result

    def get_email_body(self, msg):
        """Extrai corpo do email"""
        body = ""
        html_body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                try:
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode(errors='ignore')
                    elif content_type == "text/html" and "attachment" not in content_disposition:
                        html_body = part.get_payload(decode=True).decode(errors='ignore')
                except Exception:
                    pass
        else:
            try:
                content_type = msg.get_content_type()
                if content_type == "text/plain":
                    body = msg.get_payload(decode=True).decode(errors='ignore')
                elif content_type == "text/html":
                    html_body = msg.get_payload(decode=True).decode(errors='ignore')
            except Exception:
                pass

        return body, html_body

    def process_email(self, email_id):
        """Processa um email"""
        try:
            _, msg_data = self.imap.fetch(email_id, '(RFC822)')

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    from_email = self.decode_header_value(msg.get('from'))
                    to_email = self.decode_header_value(msg.get('to'))
                    subject = self.decode_header_value(msg.get('subject'))
                    date_str = msg.get('date')
                    body, html_body = self.get_email_body(msg)

                    email_data = {
                        'from': from_email,
                        'to': to_email,
                        'subject': subject,
                        'body': body,
                        'html_body': html_body,
                        'date': date_str,
                        'metadata': {
                            'message_id': msg.get('message-id'),
                            'email_id': email_id.decode()
                        }
                    }

                    logger.info(f"Novo email de: {from_email} | Assunto: {subject}")

                    # Salva no banco (se disponível)
                    saved_id = None
                    if self.db:
                        try:
                            saved_id = self.db.save_email(email_data)
                            logger.debug(f"Email salvo no DB com ID: {saved_id}")
                        except Exception as e:
                            logger.error(f"Erro ao salvar email no DB: {e}")
                    else:
                        logger.debug("DB nao disponivel, email nao salvo")

                    # Notifica no Telegram
                    if self.telegram and Config.ADMIN_CHAT_ID:
                        asyncio.run(self.notify_telegram(email_data))

                    return saved_id

        except Exception as e:
            logger.error(f"Erro ao processar email: {e}")
            return None

    async def notify_telegram(self, email_data):
        """Envia notificacao no Telegram"""
        try:
            body_preview = email_data['body'][:500] if email_data['body'] else "Sem conteudo texto"

            notification = (
                "<b>Novo Email Recebido!</b>\n\n"
                f"<b>De:</b> {email_data['from']}\n"
                f"<b>Para:</b> {email_data.get('to', 'N/A')}\n"
                f"<b>Assunto:</b> {email_data.get('subject', 'Sem assunto')}\n"
                f"<b>Data:</b> {email_data.get('date', 'N/A')}\n\n"
                f"<b>Previa:</b>\n{body_preview}..."
            )

            await self.telegram.send_message(
                chat_id=Config.ADMIN_CHAT_ID,
                text=notification
            )

        except Exception as e:
            logger.error(f"Erro ao enviar notificacao: {e}")

    def monitor(self):
        """Monitora emails continuamente"""
        logger.info(f"Monitorando emails a cada {Config.EMAIL_CHECK_INTERVAL} segundos...")

        while True:
            try:
                if not self.imap:
                    if not self.connect():
                        time.sleep(60)
                        continue

                self.imap.select('INBOX')

                _, messages = self.imap.search(None, 'UNSEEN')
                email_ids = messages[0].split()

                if email_ids:
                    logger.info(f"{len(email_ids)} novo(s) email(s) encontrado(s)")

                    for eid in email_ids:
                        self.process_email(eid)
                        time.sleep(1)

                time.sleep(Config.EMAIL_CHECK_INTERVAL)

            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                self.imap = None
                time.sleep(60)

    def run(self):
        """Inicia o monitor"""
        logger.info("Monitor de emails iniciado!")
        self.monitor()
