-- setup_supabase.sql
-- Execute isso no SQL Editor do Supabase

-- Tabela de Emails
CREATE TABLE IF NOT EXISTS emails (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    from_email VARCHAR(255) NOT NULL,
    to_email VARCHAR(255),
    subject TEXT,
    body TEXT,
    html_body TEXT,
    date TIMESTAMP,
    received_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'normal',
    tags TEXT[],
    metadata JSONB,
    processed_at TIMESTAMP,
    response_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Mensagens do Telegram
CREATE TABLE IF NOT EXISTS telegram_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    chat_id VARCHAR(100) NOT NULL,
    user_id BIGINT,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    message_text TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    received_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pending',
    sentiment VARCHAR(20),
    category VARCHAR(50),
    metadata JSONB,
    processed_at TIMESTAMP,
    response_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Respostas Automáticas
CREATE TABLE IF NOT EXISTS auto_responses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    trigger_type VARCHAR(50) NOT NULL, -- 'email' ou 'telegram'
    keywords TEXT[],
    response_text TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Estatísticas
CREATE TABLE IF NOT EXISTS statistics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE,
    total_emails INTEGER DEFAULT 0,
    total_telegram INTEGER DEFAULT 0,
    emails_pending INTEGER DEFAULT 0,
    telegram_pending INTEGER DEFAULT 0,
    emails_processed INTEGER DEFAULT 0,
    telegram_processed INTEGER DEFAULT 0,
    response_time_avg INTERVAL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date)
);

-- Tabela de Usuários/Contatos
CREATE TABLE IF NOT EXISTS contacts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255),
    telegram_chat_id VARCHAR(100),
    telegram_username VARCHAR(100),
    name VARCHAR(200),
    phone VARCHAR(50),
    tags TEXT[],
    metadata JSONB,
    first_contact_at TIMESTAMP DEFAULT NOW(),
    last_contact_at TIMESTAMP DEFAULT NOW(),
    total_messages INTEGER DEFAULT 0,
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_emails_status ON emails(status);
CREATE INDEX idx_emails_received_at ON emails(received_at DESC);
CREATE INDEX idx_emails_from ON emails(from_email);
CREATE INDEX idx_telegram_chat_id ON telegram_messages(chat_id);
CREATE INDEX idx_telegram_status ON telegram_messages(status);
CREATE INDEX idx_telegram_received_at ON telegram_messages(received_at DESC);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_telegram ON contacts(telegram_chat_id);

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_emails_updated_at BEFORE UPDATE ON emails
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_telegram_messages_updated_at BEFORE UPDATE ON telegram_messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Inserir respostas automáticas padrão
INSERT INTO auto_responses (trigger_type, keywords, response_text, priority) VALUES
('telegram', ARRAY['preço', 'valor', 'quanto custa', 'plano'],
 '💰 Nossos planos começam em R$ 29,90/mês!\n\n✅ Básico: R$ 29,90\n✅ Pro: R$ 59,90\n✅ Enterprise: Sob consulta\n\nQuer saber mais detalhes?', 10),

('telegram', ARRAY['suporte', 'ajuda', 'help', 'problema'],
 '🆘 Estamos aqui para ajudar!\n\nNossa equipe de suporte está disponível:\n📅 Segunda a Sexta: 9h às 18h\n📧 Email: suporte@seusite.com\n\nDescreva seu problema que retornaremos em breve!', 9),

('telegram', ARRAY['obrigado', 'valeu', 'thanks', 'agradeço'],
 '😊 Por nada! Ficamos felizes em ajudar!\n\nPrecisando de algo mais, é só chamar! 🚀', 5),

('telegram', ARRAY['oi', 'olá', 'hello', 'bom dia', 'boa tarde', 'boa noite'],
 '👋 Olá! Seja bem-vindo(a)!\n\nComo posso te ajudar hoje?', 8),

('email', ARRAY['orçamento', 'cotação', 'proposta'],
 'Olá! Obrigado pelo interesse em nossos serviços.\n\nNossa equipe comercial entrará em contato em até 24 horas com uma proposta personalizada.\n\nAtenciosamente,\nEquipe Comercial', 10);

-- View para dashboard
CREATE OR REPLACE VIEW dashboard_stats AS
SELECT
    (SELECT COUNT(*) FROM emails) as total_emails,
    (SELECT COUNT(*) FROM telegram_messages) as total_telegram,
    (SELECT COUNT(*) FROM emails WHERE status = 'pending') as emails_pending,
    (SELECT COUNT(*) FROM telegram_messages WHERE status = 'pending') as telegram_pending,
    (SELECT COUNT(*) FROM emails WHERE DATE(received_at) = CURRENT_DATE) as emails_today,
    (SELECT COUNT(*) FROM telegram_messages WHERE DATE(received_at) = CURRENT_DATE) as telegram_today,
    (SELECT COUNT(*) FROM contacts) as total_contacts;

-- Habilitar Row Level Security (RLS) - OPCIONAL, para segurança extra
-- ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE telegram_messages ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
