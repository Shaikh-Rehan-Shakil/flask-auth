# Imports
from flask import Flask, render_template, redirect, request, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# App init
app = Flask(__name__)
app.secret_key = "9920642359"

# DB config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Database model
class User(db.Model):
    # DB columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def setPassword(self, password):
        self.password = generate_password_hash(password)

    def checkPassword(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"auth {self.id}"


# Routes
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))

    return render_template("index.html")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.checkPassword(password):
        session["username"] = username
        return redirect(url_for("dashboard"))
    else:
        return render_template("index.html")


# Register
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("index", ERROR="User already exists")
    else:
        newUser = User(username=username)
        newUser.setPassword(password)
        db.session.add(newUser)
        db.session.commit()
        session["username"] = username
        return redirect(url_for("dashboard"))


# Dashboard
@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session["username"])
    else:
        return redirect(url_for("index"))


# Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))


# Run App
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
