# ☁️ Redis Cloud - Setup Passo a Passo

## 🎯 Opção Grátis para Desenvolvimento e Produção

Redis Cloud oferece **30MB gratuitos** permanentemente - perfeito para começar!

---

## 📝 PASSO 1: Criar Conta

1. **Acessar:** https://redis.com/try-free/

2. **Clicar em:** "Get started free"

3. **Preencher:**
   - Email: sstfinder@gmail.com (ou seu email)
   - First name: SST
   - Last name: Finder
   - Company: SST Finder (ou deixar em branco)

4. **Clicar em:** "Get Started"

5. **Verificar email** e ativar conta

---

## 📝 PASSO 2: Criar Subscription (Plano)

1. **No dashboard, clicar:** "New Subscription"

2. **Escolher:** "Fixed" (plano fixo)

3. **Selecionar:** "Free" (30MB)
   - Custo: $0.00/mês
   - 30MB RAM
   - 30 conexões simultâneas
   - Perfeito para desenvolvimento e produção pequena

4. **Cloud Provider:** AWS (recomendado)
   - Alternativa: GCP ou Azure

5. **Região:** Escolher mais próxima:
   - Brasil: `São Paulo (sa-east-1)` ⭐ MELHOR PARA BRASIL
   - Alternativa: `N. Virginia (us-east-1)`
   - Alternativa: `Frankfurt (eu-central-1)`

6. **Subscription name:** `sst-finder-dev`

7. **Clicar:** "Create subscription"
   - Aguardar ~2 minutos

---

## 📝 PASSO 3: Criar Database

1. **No subscription criado, clicar:** "New database"

2. **Configurações:**

   **General:**
   - Database name: `sst-notifications`
   - Protocol: Redis
   - Port: (deixar automático)

   **Security:**
   - Default user password: (gerar senha forte)
   - Exemplo: `Rf8$kL2m#pQ9x`
   - ⚠️ **COPIAR E SALVAR** esta senha!

   **Durability:**
   - Dataset persistence: `Snapshot every 1 hour` (padrão)
   - ✅ Backups automáticos

   **Advanced:**
   - Eviction policy: `allkeys-lru` (recomendado)
   - Data persistence: `Append-only file every 1 sec`

3. **Clicar:** "Activate database"
   - Aguardar ~1 minuto

---

## 📝 PASSO 4: Obter Credenciais

1. **Clicar no database criado** (`sst-notifications`)

2. **Copiar informações:**

   ```
   Public endpoint: redis-12345.c123.us-east-1-2.ec2.cloud.redislabs.com:12345

   Separar em:
   - Host: redis-12345.c123.us-east-1-2.ec2.cloud.redislabs.com
   - Port: 12345
   - Password: Rf8$kL2m#pQ9x (a senha que você criou)
   ```

3. **⚠️ IMPORTANTE:** Salvar essas credenciais em local seguro!

---

## 📝 PASSO 5: Configurar .env

Abrir arquivo: `D:\TESTE_SASS\telegram-email-saas\.env`

**Atualizar linhas do Redis:**

```env
# Redis Cloud - Produção
REDIS_HOST=redis-12345.c123.us-east-1-2.ec2.cloud.redislabs.com
REDIS_PORT=12345
REDIS_PASSWORD=Rf8$kL2m#pQ9x
REDIS_TLS=false  # Redis Cloud já é seguro

# Manter o resto igual
NOTIFICATION_CHANNEL=sst-finder:notifications
```

**EXEMPLO COMPLETO do .env:**

```env
# Python
ENVIRONMENT=production
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=5000

# Redis Cloud
REDIS_HOST=redis-12345.c123.us-east-1-2.ec2.cloud.redislabs.com
REDIS_PORT=12345
REDIS_PASSWORD=Rf8$kL2m#pQ9x
NOTIFICATION_CHANNEL=sst-finder:notifications

# Telegram
TELEGRAM_TOKEN=8325793611:AAF2ASFo77LMUv-V-lTFSZd2xJBK1XmWoCg
ADMIN_CHAT_ID=8595192278

# Email
EMAIL_USER=sstfinder@gmail.com
EMAIL_PASSWORD=rvefdmlrgxxfsnpr
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
EMAIL_CHECK_INTERVAL=60

# Supabase
SUPABASE_URL=https://ryrlmccjapdexodtepgo.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📝 PASSO 6: Testar Conexão

```bash
# Ativar ambiente virtual
cd D:\TESTE_SASS\telegram-email-saas
venv\Scripts\activate

# Criar script de teste
```

Criar arquivo: `test_redis_cloud.py`

```python
import redis
import os
from dotenv import load_dotenv

load_dotenv()

print("Testando conexão com Redis Cloud...")
print(f"Host: {os.getenv('REDIS_HOST')}")
print(f"Port: {os.getenv('REDIS_PORT')}")

try:
    # Conectar
    r = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5
    )

    # Testar ping
    response = r.ping()
    print(f"✅ Conexão bem-sucedida! Response: {response}")

    # Testar set/get
    r.set('test_key', 'SST Finder funcionando!')
    value = r.get('test_key')
    print(f"✅ Set/Get funcionando! Valor: {value}")

    # Testar pub/sub
    pubsub = r.pubsub()
    pubsub.subscribe('sst-finder:notifications')
    print("✅ Pub/Sub funcionando!")

    # Limpar
    r.delete('test_key')
    print("✅ Teste completo! Redis Cloud configurado corretamente!")

except Exception as e:
    print(f"❌ Erro: {e}")
```

```bash
# Executar teste
python test_redis_cloud.py
```

**Saída esperada:**
```
Testando conexão com Redis Cloud...
Host: redis-12345.c123.us-east-1-2.ec2.cloud.redislabs.com
Port: 12345
✅ Conexão bem-sucedida! Response: True
✅ Set/Get funcionando! Valor: SST Finder funcionando!
✅ Pub/Sub funcionando!
✅ Teste completo! Redis Cloud configurado corretamente!
```

---

## 📝 PASSO 7: Iniciar Serviço

```bash
# Iniciar serviço de notificações
python main.py
```

**Logs esperados:**
```
2026-03-05 12:30:00 - INFO - SST FINDER - NOTIFICATION SERVICE
2026-03-05 12:30:00 - INFO - Flask API rodando na porta 5000
2026-03-05 12:30:01 - INFO - Monitor de emails iniciado
2026-03-05 12:30:02 - INFO - Telegram Bot iniciado
2026-03-05 12:30:02 - INFO - Iniciando Redis Subscriber...
2026-03-05 12:30:03 - INFO - [SUBSCRIBER] Escutando canal 'sst-finder:notifications'...
```

✅ **FUNCIONANDO!** Redis Cloud conectado!

---

## 📊 Monitoramento Redis Cloud

1. **Dashboard:** https://app.redislabs.com/

2. **Métricas disponíveis:**
   - Uso de memória
   - Operações por segundo
   - Conexões ativas
   - Latência
   - Comandos executados

3. **Alertas:**
   - Configurar email quando memória > 80%
   - Configurar email quando erro de conexão

---

## 💰 Limites do Plano Free

| Recurso | Limite Free | Limite Paid ($5/mês) |
|---------|-------------|----------------------|
| **Memória** | 30 MB | 1 GB |
| **Conexões** | 30 | 256 |
| **Ops/sec** | ~10k | Ilimitado |
| **Bandwidth** | 100 MB/dia | Ilimitado |
| **Backups** | 1 por dia | Múltiplos |
| **Alta Disponibilidade** | ❌ | ✅ |
| **Multi-AZ** | ❌ | ✅ |

**Para SST Finder:** 30MB é suficiente para começar!
- ~30.000 mensagens de notificação
- ~1000 usuários ativos
- ~10.000 operações/dia

---

## 🔒 Segurança

✅ **Já implementado pelo Redis Cloud:**
- Criptografia em trânsito
- Isolamento de rede
- Autenticação por senha
- Logs de acesso
- Proteção DDoS

**Recomendações adicionais:**
- ✅ Usar senha forte (já feito)
- ✅ Não commitar .env no git (já feito - está no .gitignore)
- ✅ Rotacionar senha a cada 90 dias
- ⚠️ Opcional: IP Whitelist (limitar acesso apenas ao seu servidor)

---

## 🚀 Upgrade quando necessário

**Quando fazer upgrade?**
- Uso de memória > 25MB (80%)
- Mais de 100 conexões simultâneas
- Latência > 50ms
- Precisar alta disponibilidade (99.99% uptime)

**Como fazer upgrade?**
1. Dashboard → Subscription → Upgrade
2. Escolher plano maior
3. Sem downtime!

---

## ✅ CHECKLIST

- [ ] Conta criada no Redis Cloud
- [ ] Subscription "sst-finder-dev" criada
- [ ] Database "sst-notifications" criada
- [ ] Credenciais salvas
- [ ] .env atualizado
- [ ] Teste de conexão passou
- [ ] Serviço iniciando corretamente
- [ ] Dashboard monitorado

---

## 🆘 Troubleshooting

### Erro: "Connection timeout"
```bash
# Verificar se host/port estão corretos
ping redis-12345.c123.us-east-1-2.ec2.cloud.redislabs.com

# Verificar firewall/antivirus
# Redis Cloud usa porta personalizada (não 6379 padrão)
```

### Erro: "Authentication failed"
```bash
# Verificar senha no dashboard Redis Cloud
# Copiar senha novamente
# Atualizar .env
```

### Erro: "OOM command not allowed"
```bash
# Memória cheia (30MB)
# Limpar chaves antigas:
redis-cli -h host -p port -a senha
> FLUSHDB
# Ou fazer upgrade do plano
```

---

**Dúvidas?** Ver documentação oficial: https://docs.redis.com/latest/
