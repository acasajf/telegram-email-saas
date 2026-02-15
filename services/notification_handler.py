import logging
from pathlib import Path
from database.connection import get_user_by_id, get_user_by_email, get_admin_users

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def load_template(name: str) -> str:
    """Carrega template de mensagem do diretório templates/."""
    path = TEMPLATES_DIR / f"{name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def format_message(event: str, data: dict) -> str:
    """Formata a mensagem baseada no evento e dados."""
    template = load_template(event.replace(".", "_"))

    if template:
        try:
            return template.format(**data)
        except KeyError as e:
            logger.warning(f"Template key missing for {event}: {e}")

    # Fallback: mensagem genérica
    return format_fallback(event, data)


def format_fallback(event: str, data: dict) -> str:
    """Formata mensagem genérica quando template não existe."""
    event_labels = {
        "lead.new": "Novo Lead",
        "message.new": "Nova Mensagem",
        "contact.new": "Novo Contato",
        "user.registered": "Novo Cadastro",
        "payment.completed": "Pagamento Confirmado",
        "subscription.cancelled": "Assinatura Cancelada",
        "document.processed": "Documento Processado",
    }

    label = event_labels.get(event, event)
    details = "\n".join(f"  {k}: {v}" for k, v in data.items() if v)

    return f"SST Finder - {label}\n\n{details}"


def get_recipients(event: str, data: dict, user_id: str | None) -> list[str]:
    """Retorna lista de chat_ids que devem receber a notificação."""
    chat_ids = []

    # Eventos que notificam o usuário alvo
    if user_id:
        user = get_user_by_id(user_id)
        if user and user.get("telegramChatId") and user.get("telegramNotifications"):
            chat_ids.append(user["telegramChatId"])

    # Eventos que notificam admins
    admin_events = {"contact.new", "user.registered", "subscription.cancelled"}
    if event in admin_events:
        admins = get_admin_users()
        for admin in admins:
            if admin["telegramChatId"] and admin["telegramChatId"] not in chat_ids:
                chat_ids.append(admin["telegramChatId"])

    # Lead: notificar o profissional pelo email
    if event == "lead.new" and not chat_ids:
        prof_email = data.get("professionalEmail")
        if prof_email:
            user = get_user_by_email(prof_email)
            if user and user.get("telegramChatId") and user.get("telegramNotifications"):
                chat_ids.append(user["telegramChatId"])

    # Mensagem: notificar o destinatário pelo email
    if event == "message.new" and not chat_ids:
        to_email = data.get("toEmail")
        if to_email:
            user = get_user_by_email(to_email)
            if user and user.get("telegramChatId") and user.get("telegramNotifications"):
                chat_ids.append(user["telegramChatId"])

    return chat_ids
