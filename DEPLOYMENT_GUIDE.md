# 🚀 Guia de Deployment - SST Finder Notification Service

## 📋 Índice

- [Desenvolvimento](#desenvolvimento)
- [Produção](#producao)
- [Opções de Redis](#opcoes-de-redis)
- [Monitoramento](#monitoramento)
- [Troubleshooting](#troubleshooting)

---

## 💻 DESENVOLVIMENTO

### Opção 1: Docker Desktop (Recomendado)

#### Pré-requisitos
- Docker Desktop instalado
- Docker Compose disponível

#### Instalação Docker Desktop

```bash
# Baixar e instalar:
# https://www.docker.com/products/docker-desktop/

# Verificar instalação
docker --version
docker-compose --version
```

#### Iniciar Redis Local

```bash
# 1. Navegar até o projeto
cd D:\TESTE_SASS\telegram-email-saas

# 2. Iniciar Redis
docker-compose up -d

# 3. Verificar status
docker-compose ps

# 4. Ver logs
docker-compose logs -f redis

# 5. Testar conexão
docker exec sst-finder-redis redis-cli ping
# Deve retornar: PONG
```

#### Comandos Úteis

```bash
# Parar Redis
docker-compose down

# Reiniciar Redis
docker-compose restart

# Ver logs em tempo real
docker-compose logs -f

# Acessar Redis CLI
docker exec -it sst-finder-redis redis-cli

# Limpar dados do Redis
docker-compose down -v
```

#### Iniciar Serviço de Notificações

```bash
# Terminal 1 - Redis (já rodando via docker-compose)

# Terminal 2 - Serviço Python
cd D:\TESTE_SASS\telegram-email-saas
venv\Scripts\activate
python main.py
```

---

### Opção 2: WSL2 + Redis

#### Instalar WSL2

```bash
# PowerShell como Administrador
wsl --install
wsl --set-default-version 2
```

#### Instalar Redis no WSL

```bash
# Entrar no WSL
wsl

# Atualizar pacotes
sudo apt update && sudo apt upgrade -y

# Instalar Redis
sudo apt install redis-server -y

# Iniciar Redis
sudo service redis-server start

# Testar
redis-cli ping
# Deve retornar: PONG

# Configurar auto-start
echo "sudo service redis-server start" >> ~/.bashrc
```

#### Conectar do Windows ao Redis no WSL

```bash
# Descobrir IP do WSL
wsl hostname -I

# Atualizar .env
REDIS_HOST=172.x.x.x  # IP do WSL
REDIS_PORT=6379
```

---

### Opção 3: Memurai (Windows Nativo)

1. **Download:** https://www.memurai.com/
2. **Instalar:** Executar instalador
3. **Iniciar:** Serviço inicia automaticamente
4. **Testar:** Abrir Memurai CLI

**Vantagens:**
- ✅ Interface gráfica
- ✅ Redis nativo Windows
- ✅ Compatível 100%

**Limitações:**
- ⚠️ Versão gratuita limitada

---

### Opção 4: Redis Cloud (Desenvolvimento Grátis)

1. **Criar conta:** https://redis.com/try-free/
2. **Criar database:** Free 30MB
3. **Copiar credenciais**
4. **Atualizar .env:**

```env
REDIS_HOST=redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com
REDIS_PORT=12345
REDIS_PASSWORD=sua_senha_aqui
```

**Vantagens:**
- ✅ Zero configuração local
- ✅ Mesma solução dev + produção
- ✅ Backups automáticos

---

## 🚀 PRODUÇÃO

### Comparação de Opções

| Opção | Custo/mês | Complexidade | Recomendação |
|-------|-----------|--------------|--------------|
| **Redis Cloud** | $0 - $5+ | ⭐ Baixa | ⭐⭐⭐⭐⭐ |
| **Docker em VPS** | $5 - $20 | ⭐⭐ Média | ⭐⭐⭐⭐ |
| **AWS ElastiCache** | $15+ | ⭐⭐⭐ Alta | ⭐⭐⭐ |
| **Azure Redis** | $15+ | ⭐⭐⭐ Alta | ⭐⭐⭐ |

---

### Opção 1: Redis Cloud (Managed) ⭐ RECOMENDADO

#### Vantagens
- ✅ Alta disponibilidade automática
- ✅ Backups automáticos diários
- ✅ SSL/TLS incluído
- ✅ Monitoramento 24/7
- ✅ Escalabilidade fácil
- ✅ Zero manutenção
- ✅ Multi-region replication

#### Setup

1. **Criar conta:** https://redis.com/try-free/

2. **Criar Subscription:**
   - Fixed Plan: $5/mês (1GB)
   - Flexible Plan: Pay-as-you-go

3. **Criar Database:**
   - Protocol: Redis
   - Cloud: AWS/GCP/Azure
   - Region: Mais próxima dos usuários
   - Eviction Policy: `allkeys-lru`

4. **Configurar Segurança:**
   - Ativar TLS/SSL
   - Criar senha forte
   - Whitelist IPs (opcional)

5. **Obter Credenciais:**
   ```
   Endpoint: redis-xxxxx.c123.us-east-1.ec2.cloud.redislabs.com
   Port: 12345
   Password: *****
   ```

6. **Atualizar Variáveis de Ambiente:**
   ```env
   REDIS_HOST=redis-xxxxx.c123.us-east-1.ec2.cloud.redislabs.com
   REDIS_PORT=12345
   REDIS_PASSWORD=sua_senha_forte
   REDIS_TLS=true
   ```

#### Monitoramento

- Dashboard web com métricas
- Alertas configuráveis
- Logs de acesso
- Performance insights

---

### Opção 2: Docker em VPS (DigitalOcean/AWS/Hetzner)

#### Pré-requisitos
- VPS Ubuntu 22.04+
- Docker & Docker Compose instalados
- Domínio configurado (opcional)

#### Setup Completo

```bash
# 1. Conectar ao VPS
ssh root@seu-servidor.com

# 2. Atualizar sistema
apt update && apt upgrade -y

# 3. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# 4. Instalar Docker Compose
apt install docker-compose -y

# 5. Criar diretório do projeto
mkdir -p /opt/sst-finder
cd /opt/sst-finder

# 6. Clonar repositório ou fazer upload dos arquivos
git clone <seu-repo> .
# OU
scp -r ./telegram-email-saas/* root@servidor:/opt/sst-finder/

# 7. Criar arquivo .env de produção
nano .env
```

**.env para Produção:**
```env
# Python
ENVIRONMENT=production
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=5000

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=senha_forte_redis_123
NOTIFICATION_CHANNEL=sst-finder:notifications

# Telegram
TELEGRAM_TOKEN=seu_token_aqui
ADMIN_CHAT_ID=seu_chat_id

# Email
EMAIL_USER=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_app
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
EMAIL_CHECK_INTERVAL=60

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=sua_key_aqui
```

```bash
# 8. Build e iniciar serviços
docker-compose -f docker-compose.prod.yml up -d --build

# 9. Verificar status
docker-compose -f docker-compose.prod.yml ps

# 10. Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### Configurar Firewall

```bash
# UFW (Ubuntu)
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw allow 5000/tcp    # API (se expor publicamente)
ufw enable
```

#### Backup Automático

```bash
# Criar script de backup
nano /opt/sst-finder/backup.sh
```

**backup.sh:**
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup Redis
docker exec sst-finder-redis-prod redis-cli save
docker cp sst-finder-redis-prod:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Manter apenas últimos 7 backups
find $BACKUP_DIR -name "redis_*.rdb" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Tornar executável
chmod +x /opt/sst-finder/backup.sh

# Agendar backup diário (3h da manhã)
crontab -e
# Adicionar linha:
0 3 * * * /opt/sst-finder/backup.sh >> /var/log/redis-backup.log 2>&1
```

#### Monitoramento com Logs

```bash
# Ver logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f

# Logs específicos
docker-compose -f docker-compose.prod.yml logs -f redis
docker-compose -f docker-compose.prod.yml logs -f notification-service

# Últimas 100 linhas
docker-compose -f docker-compose.prod.yml logs --tail=100
```

---

### Opção 3: AWS ElastiCache

#### Setup Rápido

1. **Console AWS → ElastiCache**
2. **Create Redis Cluster:**
   - Engine: Redis 7.x
   - Node type: cache.t3.micro ($15/mês)
   - Replicas: 1 (alta disponibilidade)
   - Multi-AZ: Enabled

3. **Security Group:**
   - Permitir porta 6379 do seu servidor

4. **Obter Endpoint:**
   ```
   primary-endpoint.cache.amazonaws.com:6379
   ```

5. **Atualizar .env:**
   ```env
   REDIS_HOST=xxxxx.cache.amazonaws.com
   REDIS_PORT=6379
   REDIS_PASSWORD=  # Se configurado
   ```

---

## 📊 MONITORAMENTO

### Verificar Status do Redis

```bash
# Docker local
docker exec sst-finder-redis redis-cli ping

# Produção Docker
docker exec sst-finder-redis-prod redis-cli -a senha_forte ping

# Redis Cloud
redis-cli -h endpoint -p porta -a senha ping
```

### Métricas Importantes

```bash
# Informações gerais
redis-cli info

# Memória
redis-cli info memory

# Stats
redis-cli info stats

# Clientes conectados
redis-cli client list

# Monitor em tempo real
redis-cli monitor
```

### Health Check da API

```bash
# Local
curl http://localhost:5000/health

# Produção
curl https://seu-dominio.com/health
```

---

## 🔧 TROUBLESHOOTING

### Redis não conecta

```bash
# Verificar se está rodando
docker ps | grep redis

# Verificar logs
docker logs sst-finder-redis

# Testar conexão
telnet localhost 6379
```

### Serviço Python não conecta ao Redis

```bash
# Verificar variáveis de ambiente
docker exec notification-service env | grep REDIS

# Testar conexão manual
docker exec -it notification-service python
>>> import redis
>>> r = redis.Redis(host='redis', port=6379)
>>> r.ping()
```

### Alta latência

```bash
# Verificar slow log
redis-cli slowlog get 10

# Verificar memória
redis-cli info memory

# Verificar clientes
redis-cli client list
```

### Redis reiniciando

```bash
# Verificar logs do Docker
docker logs sst-finder-redis-prod

# Verificar memória do servidor
free -h

# Verificar disco
df -h
```

---

## 📈 ESCALABILIDADE

### Quando Escalar?

- Uso de memória > 70%
- Latência > 100ms
- CPU > 80%
- Mais de 1000 req/s

### Opções:

1. **Vertical:** Aumentar RAM/CPU do Redis
2. **Horizontal:** Redis Cluster (sharding)
3. **Read Replicas:** Para leituras pesadas

---

## ✅ CHECKLIST DE PRODUÇÃO

- [ ] Redis com senha forte
- [ ] TLS/SSL habilitado (Redis Cloud ou proxy)
- [ ] Backups automáticos configurados
- [ ] Monitoramento ativo
- [ ] Logs centralizados
- [ ] Firewall configurado
- [ ] Variáveis de ambiente seguras
- [ ] Health checks funcionando
- [ ] Documentação atualizada
- [ ] Plano de disaster recovery

---

## 🆘 SUPORTE

- **Redis Docs:** https://redis.io/docs/
- **Redis Cloud:** https://docs.redis.com/latest/
- **Docker Docs:** https://docs.docker.com/
- **GitHub Issues:** https://github.com/seu-repo/issues

---

**Última atualização:** 2026-03-05
**Versão:** 1.0.0
