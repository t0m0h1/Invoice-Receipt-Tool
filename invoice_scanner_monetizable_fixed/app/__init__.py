import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

# Import models for user_loader
from .models import User

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(
        __name__,
        instance_relative_config=False,
        template_folder="templates",
        static_folder="static"
    )

    # Config
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URI",
        "sqlite:///" + os.path.join(app.root_path, "app.db")
    )
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB max
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Import blueprints
    from .auth import bp as auth_bp
    from .scan import bp as scan_bp
    from .billing import bp as billing_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(billing_bp)

    # Ensure DB is created
    with app.app_context():
        db.create_all()

    # Root route
    @app.route("/")
    def index():
        return render_template("index.html")

    return app
