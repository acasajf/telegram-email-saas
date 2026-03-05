# 🏗️ Arquitetura - SST Finder Notification Service

**Última atualização:** 05/03/2026

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Componentes do Sistema](#componentes-do-sistema)
3. [Fluxo de Dados](#fluxo-de-dados)
4. [Integração com SST Finder](#integração-com-sst-finder)
5. [Tecnologias Utilizadas](#tecnologias-utilizadas)
6. [Configuração](#configuração)
7. [Deploy](#deploy)
8. [Segurança](#segurança)

---

## 🎯 Visão Geral

O **SST Finder Notification Service** é um microsserviço Python responsável por:

- ✅ **Monitorar emails** (Gmail IMAP) em busca de mensagens importantes
- ✅ **Enviar notificações** via Telegram Bot para usuários cadastrados
- ✅ **Escutar eventos** do SST Finder via Redis Pub/Sub
- ✅ **Processar automaticamente** respostas a emails recebidos
- ✅ **Fornecer API REST** para webhooks e integrações externas

### **Arquitetura High-Level**

```
┌─────────────────────────────────────────────────────────────────┐
│                     SST FINDER (Next.js)                        │
│                   http://localhost:3000                         │
└─────────────┬───────────────────────────────────────────────────┘
              │
              │ Pub/Sub Events
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         REDIS                                   │
│                  Canal: sst:notifications                       │
└─────────────┬───────────────────────────────────────────────────┘
              │
              │ Subscribe
              ▼
┌─────────────────────────────────────────────────────────────────┐
│          TELEGRAM-EMAIL-SAAS (Python Service)                   │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Redis Sub    │  │ Email Mon    │  │ Telegram Bot │         │
│  │ (Eventos SST)│  │ (Gmail IMAP) │  │ (Bot Handler)│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐          │
│  │            Flask API (REST)                      │          │
│  │            Port: 5000                            │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────┬───────────────────────────────────────────────────┘
              │
              │ Queries/Updates
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPABASE (PostgreSQL)                        │
│          Database compartilhado com SST Finder                  │
└─────────────────────────────────────────────────────────────────┘
              │
              │ Send Messages
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TELEGRAM API                               │
│              Bot: @SSTFinder_bot                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Componentes do Sistema

### **1. Redis Subscriber** (`services/redis_subscriber.py`)

**Responsabilidade:** Escutar eventos do SST Finder

**Como funciona:**
- Conecta ao Redis local (localhost:6379)
- Se inscreve no canal `sst:notifications`
- Recebe eventos publicados pelo SST Finder
- Formata e envia notificações via Telegram

**Eventos que escuta:**
```json
{
  "event": "user.registered",
  "userId": "123",
  "data": {
    "name": "João Silva",
    "email": "joao@example.com"
  }
}
```

**Exemplos de eventos:**
- `user.registered` - Novo usuário cadastrado
- `subscription.created` - Nova assinatura criada
- `payment.received` - Pagamento recebido
- `alert.critical` - Alerta crítico do sistema

---

### **2. Email Monitor** (`services/email_monitor.py`)

**Responsabilidade:** Monitorar caixa de entrada do Gmail

**Como funciona:**
- Conecta ao Gmail via IMAP SSL (porta 993)
- Verifica novos emails a cada 60 segundos (configurável)
- Processa emails não lidos
- Envia notificação para admin via Telegram
- Opcionalmente, responde automaticamente emails

**Filtros aplicados:**
- Apenas emails não lidos (UNSEEN)
- Ignora spam e lixeira
- Prioriza emails com palavras-chave específicas

**Fluxo de processamento:**
```
1. Conectar IMAP → 2. Buscar UNSEEN → 3. Parse email
      ↓                    ↓                   ↓
4. Extrair dados → 5. Formatar msg → 6. Enviar Telegram
      ↓
7. Marcar como lido (opcional)
```

---

### **3. Telegram Bot** (`services/telegram_bot.py`)

**Responsabilidade:** Interface com usuários via Telegram

**Comandos disponíveis:**
- `/start` - Inicia bot e registra usuário
- `/status` - Ver status do sistema
- `/help` - Lista de comandos
- `/subscribe` - Inscrever em notificações
- `/unsubscribe` - Cancelar notificações

**Recursos:**
- Envio de mensagens formatadas (HTML/Markdown)
- Botões interativos (InlineKeyboard)
- Respostas automáticas
- Rate limiting
- Tratamento de erros

---

### **4. Flask API** (`api/routes.py`)

**Responsabilidade:** Fornecer endpoints REST

**Endpoints:**

#### **GET `/health`**
Verificar saúde do serviço
```bash
curl http://localhost:5000/health
```
**Resposta:**
```json
{
  "status": "healthy",
  "services": {
    "telegram": "connected",
    "redis": "connected",
    "email": "connected"
  },
  "timestamp": "2026-03-05T10:30:00Z"
}
```

#### **POST `/webhook/telegram`**
Webhook para receber atualizações do Telegram
```json
{
  "update_id": 123456789,
  "message": {
    "text": "/start",
    "chat": {"id": 8595192278}
  }
}
```

#### **POST `/notify`**
Enviar notificação manual
```bash
curl -X POST http://localhost:5000/notify \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "8595192278",
    "message": "Teste de notificação"
  }'
```

---

### **5. Supabase Client** (`database/supabase_client.py`)

**Responsabilidade:** Interface com banco de dados

**Operações:**
- Buscar usuários por chat_id
- Atualizar preferências de notificação
- Registrar logs de mensagens enviadas
- Consultar estatísticas de uso

**Exemplo de uso:**
```python
from database import supabase_client

# Buscar usuário por chat_id
user = supabase_client.get_user_by_telegram_id("8595192278")

# Atualizar preferências
supabase_client.update_notification_settings(
    user_id=user['id'],
    email_notifications=True,
    telegram_notifications=True
)
```

---

## 🔄 Fluxo de Dados

### **Fluxo 1: Evento do SST Finder → Notificação Telegram**

```
1. Usuário cadastra no SST Finder (Next.js)
   ↓
2. SST Finder publica evento no Redis:
   PUBLISH sst:notifications '{"event":"user.registered","userId":"123"}'
   ↓
3. Redis Subscriber recebe evento
   ↓
4. Busca chat_id do usuário no Supabase
   ↓
5. Formata mensagem com base no evento
   ↓
6. Envia via Telegram Bot API
   ↓
7. Usuário recebe notificação no Telegram
```

### **Fluxo 2: Novo Email → Notificação Admin**

```
1. Email chega na caixa sstfinder@gmail.com
   ↓
2. Email Monitor detecta novo email (IMAP)
   ↓
3. Extrai: assunto, remetente, corpo
   ↓
4. Formata mensagem HTML
   ↓
5. Envia para ADMIN_CHAT_ID via Telegram
   ↓
6. Admin recebe alerta no Telegram
   ↓
7. Email marcado como lido (opcional)
```

### **Fluxo 3: Comando do Usuário → Resposta Bot**

```
1. Usuário envia /start no Telegram
   ↓
2. Telegram envia update para bot
   ↓
3. Bot processa comando
   ↓
4. Verifica se usuário existe no Supabase
   ↓
5. Se não existe, cria registro
   ↓
6. Envia mensagem de boas-vindas
```

---

## 🔗 Integração com SST Finder

### **Como o SST Finder envia eventos:**

No código Next.js do SST Finder:

```typescript
// src/lib/redis/publisher.ts
import Redis from 'ioredis';

const redis = new Redis({
  host: 'localhost',
  port: 6379,
});

export async function publishNotification(event: string, data: any, userId?: string) {
  const payload = {
    event,
    userId,
    data,
    timestamp: new Date().toISOString(),
  };

  await redis.publish('sst:notifications', JSON.stringify(payload));
}
```

**Uso no SST Finder:**

```typescript
// Após cadastro de usuário
await publishNotification('user.registered', {
  name: user.name,
  email: user.email,
}, user.id);

// Após pagamento
await publishNotification('payment.received', {
  amount: payment.amount,
  plan: payment.plan,
}, user.id);
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Python** | 3.14+ | Linguagem principal |
| **python-telegram-bot** | 20.7 | SDK Telegram Bot |
| **Flask** | 3.0.0 | API REST |
| **Redis** | 5.0.1 | Pub/Sub e cache |
| **Supabase** | 2.3.4 | Cliente PostgreSQL |
| **imaplib** | Built-in | Monitoramento Gmail |
| **python-dotenv** | 1.0.0 | Variáveis de ambiente |

---

## ⚙️ Configuração

### **Variáveis de Ambiente** (`.env`)

```env
# Supabase (Database)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_service_role_key
SUPABASE_SERVICE_KEY=sua_service_role_key

# Telegram
TELEGRAM_TOKEN=8325793611:AAF2ASFo77LMUv-V-lTFSZd2xJBK1XmWoCg
ADMIN_CHAT_ID=8595192278

# Gmail IMAP
EMAIL_USER=sstfinder@gmail.com
EMAIL_PASSWORD=sua_senha_app_16_caracteres
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993

# Redis (integração com SST Finder)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# SST Finder
SST_FINDER_URL=http://localhost:3000

# API Flask
API_HOST=0.0.0.0
API_PORT=5000
API_SECRET_KEY=gere_chave_secreta_aqui

# Configurações
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
EMAIL_CHECK_INTERVAL=60
AUTO_RESPONSE_ENABLED=True
```

---

## 🚀 Deploy

### **Desenvolvimento Local**

```bash
# 1. Instalar dependências
cd telegram-email-saas
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt

# 2. Configurar .env
cp .env.example .env
# Edite .env com suas credenciais

# 3. Testar conexões
python test_telegram.py
python test_gmail.py

# 4. Iniciar serviço
python main.py
```

### **Produção (Docker)**

```dockerfile
# Dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  notification-service:
    build: .
    env_file: .env
    depends_on:
      - redis
    restart: unless-stopped
    ports:
      - "5000:5000"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

**Deploy:**
```bash
docker-compose up -d
docker-compose logs -f notification-service
```

---

## 🔒 Segurança

### **Boas Práticas Implementadas:**

✅ **Variáveis de ambiente** - Credenciais nunca commitadas
✅ **`.env` no .gitignore** - Proteção de secrets
✅ **Senha de aplicativo Gmail** - Não usa senha real
✅ **HTTPS para APIs** - Comunicação criptografada
✅ **Validação de inputs** - Previne injeção
✅ **Rate limiting** - Previne abuso
✅ **Logs sanitizados** - Não expõe credenciais

### **⚠️ Avisos de Segurança:**

1. **NUNCA** commite o arquivo `.env`
2. **Troque** as senhas de aplicativo regularmente
3. **Use** API_SECRET_KEY forte em produção
4. **Habilite** autenticação JWT para API em produção
5. **Configure** firewall para portas 5000 e 6379

---

## 📊 Monitoramento

### **Logs do Sistema**

```bash
# Ver logs em tempo real
tail -f logs/notification-service.log

# Filtrar erros
grep ERROR logs/notification-service.log

# Estatísticas de eventos
grep "Evento recebido" logs/notification-service.log | wc -l
```

### **Métricas Importantes**

- Total de eventos processados
- Mensagens enviadas com sucesso
- Erros de conexão (Redis, Telegram, IMAP)
- Tempo de resposta da API
- Emails monitorados por hora

---

## 🧪 Testes

### **Scripts de Teste**

```bash
# Testar Telegram Bot
python test_telegram.py

# Testar Gmail IMAP
python test_gmail.py

# Testar API
curl http://localhost:5000/health
```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Add: nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto é parte do **SST Finder** e está sob licença proprietária.

---

## 🆘 Troubleshooting

### **Problema: Redis não conecta**
```bash
# Verificar se Redis está rodando
redis-cli ping
# Deve retornar: PONG

# Iniciar Redis
redis-server
```

### **Problema: Bot não responde**
```bash
# Verificar se token é válido
python test_telegram.py

# Ver logs do bot
grep "Telegram Bot" logs/*.log
```

### **Problema: Emails não são detectados**
```bash
# Testar conexão IMAP
python test_gmail.py

# Verificar se IMAP está habilitado no Gmail
# Settings → Forwarding and POP/IMAP → Enable IMAP
```

---

**Documentação criada por:** Claude Sonnet 4.5
**Projeto:** SST Finder - Notification Service
**Versão:** 1.0.0
**Data:** 05/03/2026
