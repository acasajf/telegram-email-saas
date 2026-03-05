"""
Teste de conexão com Redis Cloud
Verifica se as credenciais estão corretas e se o Redis está acessível
"""

import redis
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_redis_connection():
    """Testa conexão com Redis Cloud"""

    print("=" * 60)
    print("TESTE DE CONEXÃO - REDIS CLOUD")
    print("=" * 60)
    print()

    # Obter credenciais
    host = os.getenv('REDIS_HOST', 'localhost')
    port = os.getenv('REDIS_PORT', '6379')
    password = os.getenv('REDIS_PASSWORD', '')

    print(f"📍 Host: {host}")
    print(f"📍 Port: {port}")
    print(f"📍 Password: {'*' * len(password) if password else '(sem senha)'}")
    print()

    try:
        # Conectar ao Redis
        print("🔄 Conectando ao Redis Cloud...")
        r = redis.Redis(
            host=host,
            port=int(port),
            password=password if password else None,
            decode_responses=True,
            socket_timeout=10,
            socket_connect_timeout=10
        )

        # Teste 1: PING
        print("🔄 Teste 1: PING")
        response = r.ping()
        if response:
            print("✅ PING bem-sucedido!")
        else:
            print("❌ PING falhou")
            return False

        print()

        # Teste 2: SET/GET
        print("🔄 Teste 2: SET/GET")
        test_key = 'sst:test:connection'
        test_value = 'SST Finder - Redis Cloud funcionando!'

        r.set(test_key, test_value, ex=60)  # Expira em 60 segundos
        retrieved_value = r.get(test_key)

        if retrieved_value == test_value:
            print(f"✅ SET/GET funcionando!")
            print(f"   Valor armazenado: {retrieved_value}")
        else:
            print("❌ SET/GET falhou")
            return False

        print()

        # Teste 3: Pub/Sub
        print("🔄 Teste 3: Pub/Sub")
        channel = os.getenv('NOTIFICATION_CHANNEL', 'sst-finder:notifications')

        pubsub = r.pubsub()
        pubsub.subscribe(channel)
        print(f"✅ Subscrito ao canal: {channel}")

        # Publicar mensagem de teste
        r.publish(channel, '{"event":"test","data":{"message":"teste de conexão"}}')
        print("✅ Mensagem publicada no canal")

        # Receber mensagem
        message = pubsub.get_message(timeout=2)
        if message:
            print("✅ Pub/Sub funcionando!")

        pubsub.unsubscribe(channel)
        pubsub.close()

        print()

        # Teste 4: Info do servidor
        print("🔄 Teste 4: Informações do Servidor")
        info = r.info('server')
        print(f"✅ Versão Redis: {info.get('redis_version', 'N/A')}")
        print(f"✅ Modo: {info.get('redis_mode', 'N/A')}")

        print()

        # Teste 5: Memória
        print("🔄 Teste 5: Uso de Memória")
        memory_info = r.info('memory')
        used_memory = memory_info.get('used_memory_human', 'N/A')
        max_memory = memory_info.get('maxmemory_human', 'N/A')
        print(f"✅ Memória usada: {used_memory}")
        if max_memory != 'N/A' and max_memory != '0B':
            print(f"✅ Memória máxima: {max_memory}")

        print()

        # Limpar chave de teste
        r.delete(test_key)
        print("🧹 Chave de teste removida")

        print()
        print("=" * 60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        print()
        print("🎉 Redis Cloud está configurado corretamente!")
        print("🚀 Você pode iniciar o serviço com: python main.py")
        print()

        return True

    except redis.ConnectionError as e:
        print()
        print("=" * 60)
        print("❌ ERRO DE CONEXÃO")
        print("=" * 60)
        print()
        print(f"Detalhes: {e}")
        print()
        print("Possíveis causas:")
        print("1. Host ou porta incorretos")
        print("2. Firewall bloqueando conexão")
        print("3. Redis Cloud não está rodando")
        print("4. Credenciais incorretas")
        print()
        print("Verifique:")
        print("- REDIS_HOST no arquivo .env")
        print("- REDIS_PORT no arquivo .env")
        print("- REDIS_PASSWORD no arquivo .env")
        print()
        return False

    except redis.AuthenticationError as e:
        print()
        print("=" * 60)
        print("❌ ERRO DE AUTENTICAÇÃO")
        print("=" * 60)
        print()
        print(f"Detalhes: {e}")
        print()
        print("A senha está incorreta!")
        print()
        print("Verifique:")
        print("1. Acesse o dashboard do Redis Cloud")
        print("2. Vá até seu database")
        print("3. Copie a senha correta")
        print("4. Atualize REDIS_PASSWORD no arquivo .env")
        print()
        return False

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERRO INESPERADO")
        print("=" * 60)
        print()
        print(f"Tipo: {type(e).__name__}")
        print(f"Detalhes: {e}")
        print()
        return False


if __name__ == "__main__":
    success = test_redis_connection()
    sys.exit(0 if success else 1)
