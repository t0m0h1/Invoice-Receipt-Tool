import os, io, json, uuid
from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from . import db
from .models import ScanResult, User
from .utils import ocr_from_image, ocr_from_pdf, parse_invoice_text
from flask_login import current_user, login_required
from .auth_decorators import require_api_key
from .tasks import submit_background_task, TaskStatusStore

bp = Blueprint("scan", __name__, url_prefix="/scan")

ALLOWED = {"png","jpg","jpeg","pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED

@bp.route("/", methods=["POST"])
@require_api_key(optional=True)
def scan_file(user=None):
    if "file" not in request.files:
        return jsonify({"error":"no file uploaded"}), 400
    f = request.files["file"]
    if f.filename == "" or not allowed_file(f.filename):
        return jsonify({"error":"invalid filename or type"}), 400
    filename = secure_filename(f.filename)
    dest = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{uuid.uuid4().hex}_{filename}")
    f.save(dest)

    if user:
        if user.monthly_usage >= user.monthly_quota:
            return jsonify({"error":"monthly quota exceeded"}), 402

    if filename.lower().endswith(".pdf"):
        text = ocr_from_pdf(dest)
    else:
        text = ocr_from_image(dest)
    parsed = parse_invoice_text(text)
    sr = ScanResult(user_id = user.id if user else None, filename=filename, raw_text=text, parsed=json.dumps(parsed))
    db.session.add(sr)
    if user:
        user.monthly_usage = (user.monthly_usage or 0) + 1
    db.session.commit()
    return jsonify({"parsed": parsed, "id": sr.id})

@bp.route("/upload", methods=["GET","POST"])
def upload():
    # simple UI upload route that renders a form and shows result
    if request.method == "GET":
        return render_template("index.html")
    # POST
    if "file" not in request.files:
        flash("No file uploaded")
        return redirect(url_for("scan.upload"))
    f = request.files["file"]
    if f.filename == "" or not allowed_file(f.filename):
        flash("Invalid file")
        return redirect(url_for("scan.upload"))
    filename = secure_filename(f.filename)
    dest = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{uuid.uuid4().hex}_{filename}")
    f.save(dest)
    if filename.lower().endswith(".pdf"):
        text = ocr_from_pdf(dest)
    else:
        text = ocr_from_image(dest)
    parsed = parse_invoice_text(text)
    # save
    sr = ScanResult(user_id = current_user.id if current_user.is_authenticated else None,
                    filename=filename, raw_text=text, parsed=json.dumps(parsed))
    db.session.add(sr)
    if current_user.is_authenticated:
        current_user.monthly_usage = (current_user.monthly_usage or 0) + 1
    db.session.commit()
    return render_template("result.html", parsed=parsed, text=text)

@bp.route("/bulk", methods=["POST"])
@login_required
def bulk_upload():
    files = request.files.getlist("file")
    if not files:
        return "no files", 400
    task_id = submit_background_task(files, current_user.id)
    return jsonify({"task_id": task_id}), 202

@bp.route("/task/<task_id>", methods=["GET"])
@login_required
def task_status(task_id):
    status = TaskStatusStore.get_status(task_id)
    return jsonify(status)
