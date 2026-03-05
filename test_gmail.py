"""
Script de teste para verificar conexão com Gmail via IMAP
"""
import os
import imaplib
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_gmail_connection():
    """Testa conexão IMAP com Gmail"""
    print("\n" + "="*60)
    print("🔍 TESTE DE CONEXÃO - GMAIL IMAP")
    print("="*60 + "\n")

    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    imap_server = os.getenv('IMAP_SERVER', 'imap.gmail.com')
    imap_port = int(os.getenv('IMAP_PORT', 993))

    # Validar credenciais
    if not email_user or not email_password:
        print("❌ ERRO: Credenciais não configuradas!")
        print("\nConfigure no arquivo .env:")
        print("  EMAIL_USER=seuemail@gmail.com")
        print("  EMAIL_PASSWORD=sua_senha_app")
        return False

    print(f"📧 Email: {email_user}")
    print(f"🔧 Servidor: {imap_server}:{imap_port}")
    print()

    mail = None
    try:
        # Conectar ao servidor IMAP
        print("⏳ Conectando ao servidor IMAP...")
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        print("✅ Conectado ao servidor IMAP\n")

        # Fazer login
        print("⏳ Fazendo login...")
        mail.login(email_user, email_password)
        print(f"✅ Login realizado com sucesso!\n")

        # Selecionar INBOX
        print("⏳ Selecionando pasta INBOX...")
        mail.select('INBOX')
        print("✅ Pasta INBOX selecionada\n")

        # Buscar emails não lidos
        print("🔍 Buscando emails não lidos...")
        status, unread_messages = mail.search(None, 'UNSEEN')
        unread_count = len(unread_messages[0].split()) if unread_messages[0] else 0
        print(f"✅ Emails não lidos encontrados: {unread_count}\n")

        # Buscar total de emails
        print("🔍 Buscando total de emails...")
        status, all_messages = mail.search(None, 'ALL')
        total_count = len(all_messages[0].split()) if all_messages[0] else 0
        print(f"✅ Total de emails na INBOX: {total_count}\n")

        # Listar pastas disponíveis
        print("📁 Pastas disponíveis:")
        status, folders = mail.list()
        if folders:
            for folder in folders[:10]:  # Mostrar primeiras 10 pastas
                folder_str = folder.decode() if isinstance(folder, bytes) else str(folder)
                print(f"   - {folder_str}")

        print("\n" + "="*60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print("\n💡 Próximo passo: Iniciar o serviço completo")
        print("   python main.py\n")

        return True

    except imaplib.IMAP4.error as e:
        print("\n" + "="*60)
        print("❌ ERRO NA CONEXÃO")
        print("="*60)
        print(f"\nErro IMAP: {str(e)}\n")

        print("🔧 POSSÍVEIS SOLUÇÕES:")
        print("\n1. IMAP não habilitado:")
        print("   - Acesse Gmail → Configurações → Encaminhamento e POP/IMAP")
        print("   - Ative 'Ativar IMAP'")

        print("\n2. Senha incorreta:")
        print("   - Você DEVE usar senha de aplicativo")
        print("   - Não use sua senha normal do Gmail")
        print("   - Gere em: https://myaccount.google.com/apppasswords")

        print("\n3. Verificação em 2 etapas:")
        print("   - Deve estar ATIVADA para gerar senha de app")
        print("   - Ative em: https://myaccount.google.com/signinoptions/two-step-verification")

        print("\n4. Verifique o arquivo .env:")
        print("   - EMAIL_USER=seuemail@gmail.com")
        print("   - EMAIL_PASSWORD=abcd efgh ijkl mnop (senha de app)")
        print()

        return False
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERRO NA CONEXÃO")
        print("="*60)
        print(f"\nErro: {str(e)}\n")
        return False
    finally:
        if mail:
            try:
                mail.logout()
            except:
                pass

if __name__ == "__main__":
    success = test_gmail_connection()
    exit(0 if success else 1)
