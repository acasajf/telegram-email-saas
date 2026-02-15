from supabase import create_client, Client
from config import Config
from datetime import datetime


class SupabaseDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client: Client = create_client(
                Config.SUPABASE_URL,
                Config.SUPABASE_KEY
            )
        return cls._instance

    def __init__(self):
        self.client = self._instance.client

    # ==================== EMAILS ====================

    def save_email(self, email_data):
        """Salva email no banco"""
        try:
            data = {
                'from_email': email_data.get('from'),
                'to_email': email_data.get('to'),
                'subject': email_data.get('subject'),
                'body': email_data.get('body'),
                'html_body': email_data.get('html_body'),
                'date': email_data.get('date'),
                'metadata': email_data.get('metadata', {})
            }

            result = self.client.table('emails').insert(data).execute()

            if result.data:
                email_id = result.data[0]['id']
                print(f"Email salvo: {email_id}")
                self._update_contact(email=email_data.get('from'))
                return email_id

        except Exception as e:
            print(f"Erro ao salvar email: {e}")
            return None

    def get_emails(self, limit=50, status=None):
        """Busca emails"""
        try:
            query = self.client.table('emails').select('*')

            if status:
                query = query.eq('status', status)

            result = query.order('received_at', desc=True).limit(limit).execute()
            return result.data

        except Exception as e:
            print(f"Erro ao buscar emails: {e}")
            return []

    def update_email_status(self, email_id, status, response_sent=None):
        """Atualiza status do email"""
        try:
            data = {
                'status': status,
                'processed_at': datetime.now().isoformat()
            }

            if response_sent is not None:
                data['response_sent'] = response_sent

            self.client.table('emails').update(data).eq('id', email_id).execute()

        except Exception as e:
            print(f"Erro ao atualizar email: {e}")

    # ==================== TELEGRAM ====================

    def save_telegram_message(self, message_data):
        """Salva mensagem do Telegram"""
        try:
            data = {
                'chat_id': str(message_data.get('chat_id')),
                'user_id': message_data.get('user_id'),
                'username': message_data.get('username'),
                'first_name': message_data.get('first_name'),
                'last_name': message_data.get('last_name'),
                'message_text': message_data.get('text'),
                'message_type': message_data.get('type', 'text'),
                'metadata': message_data.get('metadata', {})
            }

            result = self.client.table('telegram_messages').insert(data).execute()

            if result.data:
                msg_id = result.data[0]['id']
                self._update_contact(
                    telegram_chat_id=str(message_data.get('chat_id')),
                    telegram_username=message_data.get('username'),
                    name=message_data.get('first_name')
                )
                return msg_id

        except Exception as e:
            print(f"Erro ao salvar mensagem Telegram: {e}")
            return None

    def get_telegram_messages(self, limit=50, status=None, chat_id=None):
        """Busca mensagens do Telegram"""
        try:
            query = self.client.table('telegram_messages').select('*')

            if status:
                query = query.eq('status', status)
            if chat_id:
                query = query.eq('chat_id', str(chat_id))

            result = query.order('received_at', desc=True).limit(limit).execute()
            return result.data

        except Exception as e:
            print(f"Erro ao buscar mensagens: {e}")
            return []

    def update_telegram_status(self, message_id, status, response_sent=None):
        """Atualiza status da mensagem"""
        try:
            data = {
                'status': status,
                'processed_at': datetime.now().isoformat()
            }

            if response_sent is not None:
                data['response_sent'] = response_sent

            self.client.table('telegram_messages').update(data).eq('id', message_id).execute()

        except Exception as e:
            print(f"Erro ao atualizar mensagem: {e}")

    # ==================== AUTO RESPONSES ====================

    def get_auto_response(self, trigger_type, text):
        """Busca resposta automática baseada em palavras-chave"""
        try:
            result = self.client.table('auto_responses')\
                .select('*')\
                .eq('trigger_type', trigger_type)\
                .eq('is_active', True)\
                .order('priority', desc=True)\
                .execute()

            text_lower = text.lower()

            for response in result.data:
                keywords = response.get('keywords', [])
                if any(keyword in text_lower for keyword in keywords):
                    return response['response_text']

            return None

        except Exception as e:
            print(f"Erro ao buscar auto-resposta: {e}")
            return None

    # ==================== CONTACTS ====================

    def _update_contact(self, email=None, telegram_chat_id=None, telegram_username=None, name=None):
        """Atualiza ou cria contato"""
        try:
            if email:
                existing = self.client.table('contacts').select('*').eq('email', email).execute()
            elif telegram_chat_id:
                existing = self.client.table('contacts').select('*').eq('telegram_chat_id', telegram_chat_id).execute()
            else:
                return

            if existing.data:
                contact_id = existing.data[0]['id']
                self.client.table('contacts').update({
                    'last_contact_at': datetime.now().isoformat(),
                    'total_messages': existing.data[0]['total_messages'] + 1
                }).eq('id', contact_id).execute()
            else:
                self.client.table('contacts').insert({
                    'email': email,
                    'telegram_chat_id': telegram_chat_id,
                    'telegram_username': telegram_username,
                    'name': name,
                    'total_messages': 1
                }).execute()

        except Exception as e:
            print(f"Erro ao atualizar contato: {e}")

    # ==================== SST-FINDER USERS ====================

    def get_user_by_id(self, user_id):
        """Busca usuário do sst-finder pelo ID (tabela users do Prisma)"""
        try:
            result = self.client.table('users').select(
                'id, name, email, role, "telegramChatId", "telegramNotifications"'
            ).eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar usuario: {e}")
            return None

    def get_user_by_email(self, email):
        """Busca usuário do sst-finder pelo email"""
        try:
            result = self.client.table('users').select(
                'id, name, email, role, "telegramChatId", "telegramNotifications"'
            ).eq('email', email.lower()).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar usuario: {e}")
            return None

    def get_admin_users(self):
        """Busca admins com Telegram vinculado"""
        try:
            result = self.client.table('users').select(
                'id, name, email, "telegramChatId"'
            ).in_('role', ['SUPER_ADMIN', 'ADMIN'])\
             .not_.is_('telegramChatId', 'null')\
             .eq('telegramNotifications', True)\
             .execute()
            return result.data
        except Exception as e:
            print(f"Erro ao buscar admins: {e}")
            return []

    # ==================== STATISTICS ====================

    def get_dashboard_stats(self):
        """Retorna estatísticas para dashboard"""
        try:
            result = self.client.table('dashboard_stats').select('*').execute()
            if result.data:
                return result.data[0]
            return {}
        except Exception as e:
            print(f"Erro ao buscar estatisticas: {e}")
            return {}

    def update_daily_stats(self):
        """Atualiza estatísticas diárias"""
        try:
            today = datetime.now().date()
            stats = self.get_dashboard_stats()

            self.client.table('statistics').upsert({
                'date': str(today),
                'total_emails': stats.get('total_emails', 0),
                'total_telegram': stats.get('total_telegram', 0),
                'emails_pending': stats.get('emails_pending', 0),
                'telegram_pending': stats.get('telegram_pending', 0)
            }).execute()

        except Exception as e:
            print(f"Erro ao atualizar estatisticas: {e}")
