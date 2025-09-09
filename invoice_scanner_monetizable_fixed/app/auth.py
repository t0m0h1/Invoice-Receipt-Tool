from flask import Blueprint, request, render_template, redirect, url_for, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required
bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email","").lower()
        password = request.form.get("password","")
        if not email or not password:
            flash("Missing fields")
            return redirect(url_for("auth.register"))
        if User.query.filter_by(email=email).first():
            flash("User exists")
            return redirect(url_for("auth.register"))
        user = User(email=email, password=password)
        user.generate_api_key()
        db.session.add(user); db.session.commit()
        login_user(user)
        flash("Registered")
        return redirect("/")
    return render_template("register.html")

@bp.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").lower()
        password = request.form.get("password","")
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            flash("Logged in")
            return redirect("/")
        flash("Invalid credentials")
    return render_template("login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect("/")
