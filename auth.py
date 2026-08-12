from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

from db import users_col

auth_bp = Blueprint("auth", __name__)
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "error"


class User(UserMixin):
    """Thin wrapper around a MongoDB user document so Flask-Login can use it."""

    def __init__(self, doc):
        self.doc = doc
        self.id = str(doc["_id"])
        self.name = doc.get("name")
        self.reg_no = doc.get("reg_no")
        self.college_id = doc.get("college_id")
        self.email = doc.get("email")


@login_manager.user_loader
def load_user(user_id):
    doc = users_col.find_one({"_id": ObjectId(user_id)})
    return User(doc) if doc else None


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        reg_no = request.form.get("reg_no", "").strip()
        college_id = request.form.get("college_id", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not all([name, reg_no, college_id, email, password]):
            flash("All fields are required.", "error")
            return render_template("signup.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("signup.html")

        if users_col.find_one({"email": email}):
            flash("An account with that email already exists.", "error")
            return render_template("signup.html")

        users_col.insert_one({
            "name": name,
            "reg_no": reg_no,
            "college_id": college_id,
            "email": email,
            "password_hash": generate_password_hash(password),
        })
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        doc = users_col.find_one({"email": email})
        if doc and check_password_hash(doc["password_hash"], password):
            login_user(User(doc))
            return redirect(url_for("main.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
