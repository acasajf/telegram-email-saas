"""
Script de teste para verificar conexão com Telegram Bot
"""
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

# Carregar variáveis de ambiente
load_dotenv()

async def test_telegram_bot():
    """Testa conexão com Telegram Bot"""
    print("\n" + "="*60)
    print("🤖 TESTE DE CONEXÃO - TELEGRAM BOT")
    print("="*60 + "\n")

    bot_token = os.getenv('TELEGRAM_TOKEN')
    admin_chat_id = os.getenv('ADMIN_CHAT_ID')

    # Validar credenciais
    if not bot_token:
        print("❌ ERRO: TELEGRAM_TOKEN não configurado!")
        print("\nConfigure no arquivo .env:")
        print("  TELEGRAM_TOKEN=seu_token_aqui")
        print("\nObtenha o token em: @BotFather")
        return False

    if not admin_chat_id:
        print("⚠️  AVISO: ADMIN_CHAT_ID não configurado!")
        print("Não será possível enviar mensagens de teste.")
        print("\nConfigure no arquivo .env:")
        print("  ADMIN_CHAT_ID=seu_chat_id")
        print("\nObtenha em: @userinfobot")

    print(f"🔑 Token: {bot_token[:10]}...{bot_token[-5:]}")
    if admin_chat_id:
        print(f"💬 Admin Chat ID: {admin_chat_id}")
    print()

    try:
        # Criar instância do bot
        print("⏳ Conectando ao Telegram...")
        bot = Bot(token=bot_token)

        # Obter informações do bot
        print("⏳ Verificando informações do bot...")
        me = await bot.get_me()

        print("✅ Bot conectado com sucesso!\n")
        print("📋 Informações do Bot:")
        print(f"   Nome: {me.first_name}")
        print(f"   Username: @{me.username}")
        print(f"   ID: {me.id}")
        print()

        # Testar envio de mensagem (se admin_chat_id configurado)
        if admin_chat_id:
            print("⏳ Enviando mensagem de teste...")

            message = """
🎉 *Teste de Conexão - SST Finder Bot*

✅ Bot configurado com sucesso!

Este é um teste automático do sistema de notificações.

🔧 Comandos disponíveis:
• /start - Iniciar bot
• /status - Ver status
• /help - Ajuda

_Sistema: SST Finder Notification Service_
"""

            await bot.send_message(
                chat_id=admin_chat_id,
                text=message,
                parse_mode='Markdown'
            )

            print("✅ Mensagem de teste enviada!\n")
            print("📱 Verifique seu Telegram para confirmar o recebimento.\n")

        print("="*60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("="*60)

        if not admin_chat_id:
            print("\n💡 Próximo passo:")
            print("   1. Configure ADMIN_CHAT_ID no .env")
            print("   2. Execute este teste novamente")
        else:
            print("\n💡 Próximo passo:")
            print("   python test_gmail.py")
        print()

        return True

    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERRO NA CONEXÃO")
        print("="*60)
        print(f"\nErro: {str(e)}\n")

        print("🔧 POSSÍVEIS SOLUÇÕES:")

        print("\n1. Token incorreto:")
        print("   - Verifique se copiou o token completo")
        print("   - Formato correto: número:letras_números")
        print("   - Obtenha novo token em: @BotFather → /token")

        print("\n2. Bot desativado:")
        print("   - Fale com @BotFather")
        print("   - Envie /mybots")
        print("   - Selecione seu bot")
        print("   - Verifique se está ativo")

        print("\n3. Problema de rede:")
        print("   - Verifique sua conexão com internet")
        print("   - Telegram pode estar bloqueado")
        print()

        return False

if __name__ == "__main__":
    success = asyncio.run(test_telegram_bot())
    exit(0 if success else 1)
