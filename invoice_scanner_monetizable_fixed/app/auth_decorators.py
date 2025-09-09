from functools import wraps
from flask import request, jsonify
from .models import User
from flask_login import current_user

def require_api_key(optional=False):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            api_key = request.headers.get("X-API-KEY") or request.form.get("api_key") or request.args.get("api_key")
            user = None
            if api_key:
                user = User.query.filter_by(api_key=api_key).first()
                if not user:
                    return jsonify({"error":"invalid api key"}), 403
            elif current_user and current_user.is_authenticated:
                user = current_user
            elif not optional:
                return jsonify({"error":"api key required"}), 401
            return f(user=user, *args, **kwargs)
        return wrapped
    return decorator
