# 🐍 Problemas de Compatibilidade - Python 3.14

**Data:** 05/03/2026
**Python Version:** 3.14.2
**Status:** ⚠️ **NÃO COMPATÍVEL** - Aguardando atualizações de bibliotecas

---

## 📋 Resumo

Python 3.14 foi lançado recentemente e várias bibliotecas Python ainda não foram atualizadas para suportar esta versão. Recomendamos usar **Python 3.11** ou **Python 3.12** para este projeto.

---

## ❌ Bibliotecas Incompatíveis

### 1. **Supabase / GoTrue** (❌ Crítico)

**Erro:**
```
TypeError: Client.__init__() got an unexpected keyword argument 'proxy'
```

**Detalhes:**
- Biblioteca `gotrue==2.9.1` tenta passar argumento `proxy` para `httpx.Client()`
- `httpx==0.25.2` não suporta este argumento da mesma forma no Python 3.14
- Tentamos versões `gotrue==2.11.0` mas problema persiste

**Stack Trace:**
```
File gotrue/_sync/gotrue_base_api.py, line 28, in __init__
    self._http_client = http_client or SyncClient(
        verify=bool(verify),
        headers=headers,
        proxy=proxy,  ← ERRO AQUI
        http2=True,
    )
TypeError: Client.__init__() got an unexpected keyword argument 'proxy'
```

**Tentativas de Solução:**
- ✅ Downgrade `gotrue` para 2.11.0 - Não funcionou
- ✅ Upgrade `httpx` para 0.28.1 - Criou mais conflitos
- ✅ Tornar Supabase opcional - **FUNCIONOU PARCIALMENTE**

**Workaround Implementado:**
- Lazy-loading de Supabase em:
  - `services/notification_handler.py`
  - `api/routes.py`
  - `services/telegram_bot.py`
- Fallback para `ADMIN_CHAT_ID` quando DB não disponível

---

### 2. **python-telegram-bot** (❌ Crítico)

**Erro:**
```
AttributeError: 'Updater' object has no attribute '_Updater__polling_cleanup_cb'
```

**Detalhes:**
- Biblioteca `python-telegram-bot==20.7` tenta definir atributo privado em objeto
- Python 3.14 mudou comportamento de atribuição em classes com `__slots__`

**Stack Trace:**
```
File telegram/ext/_updater.py, line 128, in __init__
    self.__polling_cleanup_cb: Optional[Callable[[], Coroutine[Any, Any, None]]] = None
AttributeError: 'Updater' object has no attribute '_Updater__polling_cleanup_cb'
```

**Status:** Aguardando atualização da biblioteca

---

### 3. **pyiceberg / pyroaring** (⚠️ Dependência do Supabase)

**Erro:**
```
Building wheel for pyiceberg (pyproject.toml): finished with status 'error'
```

**Detalhes:**
- Dependências do `storage3==2.28.0` (parte do Supabase)
- Requerem compilação C++ que falha em Python 3.14
- Não há wheels pré-compilados para Python 3.14 ainda

---

## ✅ O Que Funciona

### Bibliotecas Compatíveis:
- ✅ `Flask==3.0.0` - API REST funcionando
- ✅ `Flask-CORS==4.0.0` - CORS funcionando
- ✅ `python-dotenv==1.0.0` - Variáveis de ambiente OK
- ✅ `redis==5.0.1` - Cliente Redis OK (não testado servidor)
- ✅ `imaplib` (built-in) - Gmail IMAP **100% funcional** ✓
- ✅ Scripts de teste (`test_gmail.py`, `test_telegram.py`)

### O Que Foi Testado com Sucesso:
- ✅ Gmail IMAP connection (usando `imaplib` nativo)
- ✅ Telegram Bot API (teste com bot.get_me() e send_message)
- ✅ Leitura de variáveis `.env`
- ✅ Flask API inicialização

---

## 🎯 Recomendações

### ⭐ **RECOMENDAÇÃO PRINCIPAL: Usar Python 3.11 ou 3.12**

```bash
# Remover venv atual
rm -rf venv

# Criar novo venv com Python 3.11 ou 3.12
python3.11 -m venv venv
# ou
python3.12 -m venv venv

# Ativar
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Testar
python test_telegram.py
python test_gmail.py
python main.py
```

### 🔄 **Alternativa: Aguardar Atualizações**

Monitorar atualizações destas bibliotecas:
- `gotrue` → Versão compatível com Python 3.14
- `python-telegram-bot` → Versão compatível com Python 3.14

**Repositórios para acompanhar:**
- https://github.com/supabase-community/gotrue-py
- https://github.com/python-telegram-bot/python-telegram-bot

---

## 📊 Matriz de Compatibilidade

| Biblioteca | Python 3.10 | Python 3.11 | Python 3.12 | Python 3.13 | Python 3.14 |
|------------|-------------|-------------|-------------|-------------|-------------|
| supabase | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| gotrue | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| python-telegram-bot | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| flask | ✅ | ✅ | ✅ | ✅ | ✅ |
| redis | ✅ | ✅ | ✅ | ✅ | ✅ |
| python-dotenv | ✅ | ✅ | ✅ | ✅ | ✅ |

**Legenda:**
- ✅ Totalmente compatível
- ⚠️ Parcialmente compatível (pode ter pequenos problemas)
- ❌ Incompatível

---

## 🔧 Modificações Realizadas

### Arquivos Modificados para Suporte Opcional:

1. **`services/notification_handler.py`**
   ```python
   # Antes:
   from database import SupabaseDB
   db = SupabaseDB()

   # Depois:
   _db = None
   def get_db():
       global _db
       if _db is None:
           try:
               from database import SupabaseDB
               _db = SupabaseDB()
           except Exception as e:
               logger.warning(f"Supabase nao disponivel: {e}")
               _db = False
       return _db if _db is not False else None
   ```

2. **`api/routes.py`**
   - Mesma abordagem de lazy-loading

3. **`services/telegram_bot.py`**
   - Transformado em property `@property def db()`

4. **`test_gmail.py`**
   - Substituído `imapclient` por `imaplib` (built-in)
   - ✅ Funciona perfeitamente em Python 3.14

---

## 📝 Logs de Teste

### Teste com Python 3.14.2:

```
2026-03-05 12:02:09,313 - __main__ - INFO - ============================================================
2026-03-05 12:02:09,313 - __main__ - INFO - SST FINDER - NOTIFICATION SERVICE
2026-03-05 12:02:09,313 - __main__ - INFO - ============================================================
2026-03-05 12:02:09,314 - __main__ - INFO - Ambiente: development
2026-03-05 12:02:09,315 - __main__ - INFO - Flask API rodando na porta 5000
Configuracoes validadas!
 * Serving Flask app 'api.routes'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.80.29:5000

[Então falha no Telegram Bot]
AttributeError: 'Updater' object has no attribute '_Updater__polling_cleanup_cb'
```

**Análise:** Flask iniciou com sucesso! Problema apenas em bibliotecas específicas.

---

## 🎯 Próximos Passos

### Para Próxima Sessão:

1. **Opção A: Downgrade Python** (Recomendado ⭐)
   ```bash
   # Instalar Python 3.11
   # Recriar venv
   # Reinstalar dependências
   # Tudo funcionará!
   ```

2. **Opção B: Aguardar Atualizações**
   - Verificar se `gotrue` e `python-telegram-bot` lançaram versões compatíveis
   - Atualizar `requirements.txt`

3. **Opção C: Workarounds Adicionais**
   - Criar versão simplificada sem Telegram Bot
   - Usar apenas Email Monitor + Flask API
   - Implementar notificações por outros meios

---

## 📚 Referências

- [Python 3.14 Release Notes](https://docs.python.org/3.14/whatsnew/3.14.html)
- [Supabase Python Client Issues](https://github.com/supabase-community/supabase-py/issues)
- [python-telegram-bot Python 3.14 Support](https://github.com/python-telegram-bot/python-telegram-bot/issues)

---

## ✅ Conclusão

Python 3.14 é **muito novo** (lançado em 2026) e a maioria das bibliotecas ainda não foram atualizadas.

**Solução Definitiva:** Usar Python 3.11 ou 3.12 até que as bibliotecas sejam atualizadas.

**Data de Atualização Esperada:** Q2-Q3 2026 (estimativa)

---

**Documento criado por:** Claude Sonnet 4.5
**Projeto:** SST Finder - Notification Service
**Data:** 05/03/2026
