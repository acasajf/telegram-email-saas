"""
Script de teste para verificar conexão com Gmail via IMAP
"""
import os
from dotenv import load_dotenv
from imapclient import IMAPClient

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

    try:
        # Conectar ao servidor IMAP
        print("⏳ Conectando ao servidor IMAP...")
        with IMAPClient(imap_server, port=imap_port, ssl=True) as client:
            print("✅ Conectado ao servidor IMAP\n")

            # Fazer login
            print("⏳ Fazendo login...")
            client.login(email_user, email_password)
            print(f"✅ Login realizado com sucesso!\n")

            # Selecionar INBOX
            print("⏳ Selecionando pasta INBOX...")
            client.select_folder('INBOX')
            print("✅ Pasta INBOX selecionada\n")

            # Buscar emails não lidos
            print("🔍 Buscando emails não lidos...")
            unread_messages = client.search(['UNSEEN'])
            print(f"✅ Emails não lidos encontrados: {len(unread_messages)}\n")

            # Buscar total de emails
            print("🔍 Buscando total de emails...")
            all_messages = client.search(['ALL'])
            print(f"✅ Total de emails na INBOX: {len(all_messages)}\n")

            # Listar pastas disponíveis
            print("📁 Pastas disponíveis:")
            folders = client.list_folders()
            for flags, delimiter, folder_name in folders:
                print(f"   - {folder_name}")

            print("\n" + "="*60)
            print("✅ TESTE CONCLUÍDO COM SUCESSO!")
            print("="*60)
            print("\n💡 Próximo passo: Iniciar o serviço completo")
            print("   python main.py\n")

            return True

    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERRO NA CONEXÃO")
        print("="*60)
        print(f"\nErro: {str(e)}\n")

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

if __name__ == "__main__":
    success = test_gmail_connection()
    exit(0 if success else 1)
