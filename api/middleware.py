import logging
from functools import wraps
from flask import request, jsonify
from config import Config

logger = logging.getLogger(__name__)


def require_api_key(f):
    """Middleware para proteger endpoints com API key."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != Config.API_SECRET_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
