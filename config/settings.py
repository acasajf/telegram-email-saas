import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

    # Telegram
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

    # Email - IMAP
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
    IMAP_PORT = int(os.getenv('IMAP_PORT', 993))

    # Redis (integração com sst-finder)
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    NOTIFICATION_CHANNEL = 'sst:notifications'

    # SST Finder API
    SST_FINDER_URL = os.getenv('SST_FINDER_URL', 'http://localhost:3000')

    # API
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'dev-secret-key')

    # Settings
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Processing
    EMAIL_CHECK_INTERVAL = int(os.getenv('EMAIL_CHECK_INTERVAL', 60))
    AUTO_RESPONSE_ENABLED = os.getenv('AUTO_RESPONSE_ENABLED', 'True').lower() == 'true'

    @classmethod
    def validate(cls):
        """Valida configurações obrigatórias"""
        required = [
            'SUPABASE_URL',
            'SUPABASE_KEY',
            'TELEGRAM_TOKEN',
        ]

        missing = [key for key in required if not getattr(cls, key)]

        if missing:
            raise ValueError(f"Configuracoes faltando: {', '.join(missing)}")

        # Avisos para opcionais
        if not cls.EMAIL_USER or not cls.EMAIL_PASSWORD:
            print("IMAP nao configurado. Monitor de emails desativado.")

        if not cls.ADMIN_CHAT_ID:
            print("ADMIN_CHAT_ID nao configurado. Notificacoes admin desativadas.")

        print("Configuracoes validadas!")
