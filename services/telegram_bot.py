from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TelegramBotService:
    def __init__(self):
        self._db = None
        self.app = Application.builder().token(Config.TELEGRAM_TOKEN).build()
        self._setup_handlers()

    @property
    def db(self):
        """Lazy-load do database."""
        if self._db is None:
            try:
                from database import SupabaseDB
                self._db = SupabaseDB()
                logger.info("Supabase conectado no Telegram Bot")
            except Exception as e:
                logger.warning(f"Supabase nao disponivel no bot: {e}")
                self._db = False
        return self._db if self._db is not False else None

    def _setup_handlers(self):
        """Configura handlers do bot"""
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("stats", self.cmd_stats))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        chat_id = update.effective_chat.id
        user = update.effective_user

        welcome = (
            f"Ola, {user.first_name}!\n\n"
            f"Bem-vindo ao SST Finder Bot!\n\n"
            f"<b>Seu Chat ID:</b> <code>{chat_id}</code>\n\n"
            f"Envie qualquer mensagem e nossa equipe respondera em breve.\n\n"
            f"<b>Comandos disponiveis:</b>\n"
            f"/start - Iniciar conversa\n"
            f"/help - Ajuda\n"
            f"/stats - Estatisticas (admin)"
        )

        await update.message.reply_text(welcome, parse_mode='HTML')

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        help_text = (
            "<b>Como usar:</b>\n\n"
            "1. Envie sua mensagem\n"
            "2. Aguarde nossa resposta\n"
            "3. Continue a conversa naturalmente\n\n"
            "<b>Horario de atendimento:</b>\n"
            "Segunda a Sexta: 9h as 18h\n\n"
            "<b>Email:</b> contato@sstfinder.com\n"
            "<b>Site:</b> sstfinder.com"
        )

        await update.message.reply_text(help_text, parse_mode='HTML')

    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stats (apenas admin)"""
        chat_id = update.effective_chat.id

        if str(chat_id) != Config.ADMIN_CHAT_ID:
            await update.message.reply_text("Comando disponivel apenas para administradores.")
            return

        stats = self.db.get_dashboard_stats()

        stats_text = (
            "<b>Estatisticas do Sistema</b>\n\n"
            f"<b>Emails:</b>\n"
            f"  Total: {stats.get('total_emails', 0)}\n"
            f"  Pendentes: {stats.get('emails_pending', 0)}\n"
            f"  Hoje: {stats.get('emails_today', 0)}\n\n"
            f"<b>Telegram:</b>\n"
            f"  Total: {stats.get('total_telegram', 0)}\n"
            f"  Pendentes: {stats.get('telegram_pending', 0)}\n"
            f"  Hoje: {stats.get('telegram_today', 0)}\n\n"
            f"<b>Contatos:</b> {stats.get('total_contacts', 0)}\n\n"
            f"Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )

        await update.message.reply_text(stats_text, parse_mode='HTML')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens de texto"""
        message_data = {
            'chat_id': update.effective_chat.id,
            'user_id': update.effective_user.id,
            'username': update.effective_user.username,
            'first_name': update.effective_user.first_name,
            'last_name': update.effective_user.last_name,
            'text': update.message.text,
            'type': 'text',
            'metadata': {
                'message_id': update.message.message_id,
                'date': update.message.date.isoformat()
            }
        }

        # Salva no banco
        msg_id = self.db.save_telegram_message(message_data)

        # Busca resposta automatica
        if Config.AUTO_RESPONSE_ENABLED:
            auto_response = self.db.get_auto_response('telegram', message_data['text'])

            if auto_response:
                await update.message.reply_text(auto_response, parse_mode='HTML')

                if msg_id:
                    self.db.update_telegram_status(msg_id, 'processed', response_sent=True)
                return

        # Resposta padrao
        await update.message.reply_text(
            "Recebemos sua mensagem!\nNossa equipe respondera em breve. Obrigado!"
        )

        # Notifica admin
        await self.notify_admin_new_message(message_data)

    async def notify_admin_new_message(self, message_data):
        """Notifica admin sobre nova mensagem"""
        if not Config.ADMIN_CHAT_ID:
            return

        try:
            notification = (
                "<b>Nova Mensagem Recebida!</b>\n\n"
                f"<b>De:</b> {message_data['first_name']}\n"
                f"<b>Username:</b> @{message_data.get('username', 'N/A')}\n"
                f"<b>Chat ID:</b> <code>{message_data['chat_id']}</code>\n\n"
                f"<b>Mensagem:</b>\n{message_data['text']}\n\n"
                f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )

            await self.app.bot.send_message(
                chat_id=Config.ADMIN_CHAT_ID,
                text=notification,
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Erro ao notificar admin: {e}")

    async def send_message(self, chat_id, text, parse_mode='HTML'):
        """Envia mensagem para um chat"""
        try:
            await self.app.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode
            )
            return True
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            return False

    def run(self):
        """Inicia o bot"""
        print("Bot do Telegram iniciado!")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
