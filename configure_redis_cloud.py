"""
Script interativo para configurar Redis Cloud no .env
"""

import os
import re

def configure_redis_cloud():
    print("=" * 60)
    print("CONFIGURAÇÃO REDIS CLOUD - ATUALIZAR .env")
    print("=" * 60)
    print()

    # Obter credenciais do usuário
    print("Cole as informações do Redis Cloud:")
    print()

    endpoint = input("📍 Public endpoint (ex: redis-12345.c123.us-east-1.ec2.cloud.redislabs.com:12345): ").strip()

    if ':' in endpoint:
        host, port = endpoint.rsplit(':', 1)
    else:
        host = endpoint
        port = input("📍 Port (ex: 12345): ").strip()

    password = input("🔒 Password: ").strip()

    print()
    print("Credenciais recebidas:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Password: {'*' * len(password)}")
    print()

    confirm = input("Confirma atualização do .env? (s/n): ").strip().lower()

    if confirm != 's':
        print("❌ Operação cancelada")
        return

    # Ler .env
    env_path = '.env'

    if not os.path.exists(env_path):
        print(f"❌ Arquivo {env_path} não encontrado!")
        return

    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Atualizar variáveis Redis
    content = re.sub(
        r'REDIS_HOST=.*',
        f'REDIS_HOST={host}',
        content
    )

    content = re.sub(
        r'REDIS_PORT=.*',
        f'REDIS_PORT={port}',
        content
    )

    content = re.sub(
        r'REDIS_PASSWORD=.*',
        f'REDIS_PASSWORD={password}',
        content
    )

    # Escrever .env atualizado
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print()
    print("=" * 60)
    print("✅ ARQUIVO .env ATUALIZADO COM SUCESSO!")
    print("=" * 60)
    print()
    print("📝 Próximo passo:")
    print("   python test_redis_cloud.py")
    print()

if __name__ == "__main__":
    try:
        configure_redis_cloud()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
