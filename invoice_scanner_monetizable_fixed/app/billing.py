from flask import Blueprint, request, render_template, flash, redirect, url_for
from . import db
from .models import User
from flask_login import login_required, current_user

bp = Blueprint("billing", __name__, url_prefix="/billing")

@bp.route("/plans")
def plans():
    plans = [{"id":"free","name":"Free","price":0,"quota":50},{"id":"pro","name":"Pro","price":1000,"quota":5000}]
    return render_template("plans.html", plans=plans)

@bp.route("/subscribe", methods=["POST"])
@login_required
def subscribe():
    plan = request.form.get("plan")
    current_user.plan = plan
    if plan == "pro":
        current_user.monthly_quota = 5000
    else:
        current_user.monthly_quota = 50
    db.session.commit()
    flash("Subscribed (placeholder)")
    return redirect(url_for("billing.plans"))
