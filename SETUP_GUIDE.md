# 🚀 Guia de Configuração - Telegram + Email

**Última atualização:** 05/03/2026

---

## 📋 Pré-requisitos

- [ ] Python 3.8+ instalado
- [ ] Conta Gmail
- [ ] Conta Telegram
- [ ] Acesso ao Supabase do SST Finder

---

## 1️⃣ Configurar Bot do Telegram

### **Criar Bot:**

1. Abra o Telegram e procure por: **@BotFather**

2. Envie o comando: `/newbot`

3. Escolha um **nome** para o bot:
   ```
   SST Finder Bot
   ```

4. Escolha um **username** (deve terminar com "bot"):
   ```
   sstfinder_bot
   ```

5. **Copie o token** que aparece (algo como):
   ```
   7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
   ```

6. **Guarde esse token!** Você vai precisar dele no `.env`

### **Obter seu Chat ID:**

1. Procure por: **@userinfobot** no Telegram

2. Envie qualquer mensagem

3. O bot vai responder com seu **Chat ID** (exemplo: `123456789`)

4. **Guarde esse ID!** Você vai precisar dele no `.env`

---

## 2️⃣ Configurar Gmail

### **Habilitar IMAP:**

1. Acesse: https://mail.google.com

2. Clique em **⚙️ Configurações** → **Ver todas as configurações**

3. Vá na aba: **Encaminhamento e POP/IMAP**

4. Marque: ☑️ **Ativar IMAP**

5. Clique em **Salvar alterações**

### **Ativar Verificação em 2 Etapas:**

1. Acesse: https://myaccount.google.com/signinoptions/two-step-verification

2. Clique em **"Começar"**

3. Siga as instruções (vai pedir seu celular)

4. Conclua a configuração

### **Gerar Senha de Aplicativo:**

⚠️ **MUITO IMPORTANTE:** Você NÃO pode usar sua senha normal do Gmail!

1. Acesse: https://myaccount.google.com/apppasswords

2. Se pedir, faça login novamente

3. Selecione:
   - **App:** Outro (nome personalizado)
   - Digite: `SST Finder Email Monitor`

4. Clique em **Gerar**

5. **COPIE A SENHA** gerada (16 caracteres)
   ```
   Exemplo: abcd efgh ijkl mnop
   ```

6. ⚠️ **Guarde essa senha!** Ela não aparece novamente!

---

## 3️⃣ Configurar Variáveis de Ambiente

### **Criar arquivo .env:**

1. Copie o arquivo de exemplo:
   ```bash
   cp .env.example .env
   ```

2. Edite o arquivo `.env` com suas credenciais

### **Template .env completo:**

```env
# ==========================================
# SUPABASE (mesmo do SST Finder)
# ==========================================
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_service_key
SUPABASE_SERVICE_KEY=sua_service_key

# ==========================================
# TELEGRAM
# ==========================================
TELEGRAM_TOKEN=7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
ADMIN_CHAT_ID=123456789

# ==========================================
# EMAIL - GMAIL
# ==========================================
EMAIL_USER=seuemail@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993

# ==========================================
# REDIS (mesmo do SST Finder)
# ==========================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# ==========================================
# SST FINDER
# ==========================================
SST_FINDER_URL=http://localhost:3000

# ==========================================
# API FLASK
# ==========================================
API_HOST=0.0.0.0
API_PORT=5000
API_SECRET_KEY=sua_chave_secreta_aqui_gere_uma

# ==========================================
# CONFIGURAÇÕES
# ==========================================
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# ==========================================
# PROCESSAMENTO
# ==========================================
EMAIL_CHECK_INTERVAL=60
AUTO_RESPONSE_ENABLED=True
```

### **Onde encontrar cada valor:**

| Variável | Onde encontrar |
|----------|----------------|
| `SUPABASE_URL` | Dashboard Supabase → Project Settings → API |
| `SUPABASE_KEY` | Dashboard Supabase → Project Settings → API → service_role key |
| `TELEGRAM_TOKEN` | @BotFather (passo 1) |
| `ADMIN_CHAT_ID` | @userinfobot (passo 1) |
| `EMAIL_USER` | Seu email do Gmail |
| `EMAIL_PASSWORD` | Senha de app gerada (passo 2) |

---

## 4️⃣ Instalar Dependências

```bash
cd telegram-email-saas

# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

---

## 5️⃣ Testar Configuração

### **Teste 1: Conexão Gmail**

```bash
python test_gmail.py
```

**Resultado esperado:**
```
✅ Conectado ao servidor IMAP
✅ Login realizado com sucesso!
✅ Pasta INBOX selecionada
✅ Emails não lidos encontrados: 5
✅ TESTE CONCLUÍDO COM SUCESSO!
```

### **Teste 2: Bot Telegram (adicionar depois)**

```bash
python test_telegram.py
```

---

## 6️⃣ Iniciar Serviço

```bash
python main.py
```

**Logs esperados:**
```
============================================================
SST FINDER - NOTIFICATION SERVICE
============================================================
Ambiente: development
Flask API rodando na porta 5000
Monitor de emails iniciado
Telegram Bot iniciado
Iniciando Redis Subscriber...
```

---

## 🔧 Troubleshooting

### **Erro: "Invalid credentials" (Gmail)**

❌ **Problema:** Senha incorreta

✅ **Solução:**
- Verifique se usou **senha de aplicativo** (não senha normal)
- Copie a senha sem espaços
- Verifique se 2FA está ativado

### **Erro: "IMAP disabled"**

❌ **Problema:** IMAP não habilitado

✅ **Solução:**
- Gmail → Configurações → Encaminhamento e POP/IMAP
- Ativar IMAP
- Aguardar 5 minutos

### **Erro: "Bot token invalid"**

❌ **Problema:** Token do Telegram incorreto

✅ **Solução:**
- Verifique se copiou o token completo
- Não deve ter espaços no início/fim
- Formato: `número:letras_e_números`

---

## ✅ Checklist Final

- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` criado e configurado
- [ ] Bot Telegram criado (@BotFather)
- [ ] Chat ID obtido (@userinfobot)
- [ ] IMAP habilitado no Gmail
- [ ] Verificação em 2 etapas ativada
- [ ] Senha de aplicativo gerada
- [ ] Teste do Gmail passou (`python test_gmail.py`)
- [ ] Serviço iniciado (`python main.py`)

---

## 📞 Próximos Passos

Após configurar tudo:

1. **Testar fluxo completo:**
   - Enviar email para sua conta Gmail
   - Verificar notificação no Telegram
   - Verificar registro no Supabase

2. **Integrar com SST Finder:**
   - Configurar Redis Pub/Sub
   - Testar eventos de cadastro
   - Sincronizar com banco de dados

3. **Personalizar:**
   - Templates de mensagens
   - Filtros de email
   - Comandos do bot

---

**Dúvidas?** Consulte a documentação completa em `TELEGRAM_EMAIL_INTEGRATION.md`
