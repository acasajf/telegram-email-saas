from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import SupabaseDB
import redis

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = Config.API_SECRET_KEY

db = SupabaseDB()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check do servico."""
    checks = {"api": True, "supabase": False, "redis": False}

    # Check Supabase
    try:
        db.client.table('contacts').select('id').limit(1).execute()
        checks["supabase"] = True
    except Exception:
        pass

    # Check Redis
    try:
        r = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD,
        )
        r.ping()
        checks["redis"] = True
    except Exception:
        pass

    healthy = all(checks.values())
    return jsonify({"status": "healthy" if healthy else "degraded", "checks": checks})


@app.route('/stats', methods=['GET'])
def stats():
    """Estatisticas do servico."""
    try:
        dashboard = db.get_dashboard_stats()
        return jsonify(dashboard)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/emails', methods=['GET'])
def get_emails():
    """Lista emails recentes."""
    try:
        emails = db.get_emails(limit=20)
        return jsonify({"emails": emails, "count": len(emails)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/messages', methods=['GET'])
def get_messages():
    """Lista mensagens Telegram recentes."""
    try:
        messages = db.get_telegram_messages(limit=20)
        return jsonify({"messages": messages, "count": len(messages)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
