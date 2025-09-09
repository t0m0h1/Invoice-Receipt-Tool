from . import db
from flask_login import UserMixin
from datetime import datetime
import uuid

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    plan = db.Column(db.String(50), default="free")
    monthly_quota = db.Column(db.Integer, default=50)
    monthly_usage = db.Column(db.Integer, default=0)

    def generate_api_key(self):
        self.api_key = uuid.uuid4().hex

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    filename = db.Column(db.String(300))
    raw_text = db.Column(db.Text)
    parsed = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
