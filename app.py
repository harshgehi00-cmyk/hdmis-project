from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import random

load_dotenv()

app = Flask(__name__)

app.secret_key = "hdmis_secret"

# DATABASE

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///database.db"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================================
# USER TABLE
# =========================================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200))

    email = db.Column(db.String(200), unique=True)

    password = db.Column(db.String(200))

    mobile = db.Column(db.String(20))

    role = db.Column(db.String(50))

# =========================================
# APPOINTMENT TABLE
# =========================================

class Appointment(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    patient = db.Column(db.String(200))

    doctor = db.Column(db.String(200))

    date = db.Column(db.String(100))

    status = db.Column(db.String(100))

# =========================================
# CREATE DATABASE
# =========================================

with app.app_context():
    db.create_all()

# =========================================
# HOME
# =========================================

@app.route("/")
def home():
    return redirect("/login")

# =========================================
# REGISTER
# =========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]

        mobile = request.form["mobile"]

        role = request.form["role"]

        existing = User.query.filter_by(email=email).first()

        if existing:

            flash("Email already exists")

            return redirect("/register")

        otp = random.randint(1000, 9999)

        session["otp"] = str(otp)

        session["temp_user"] = {
            "name": name,
            "email": email,
            "password": password,
            "mobile": mobile,
            "role": role
        }

        print("OTP:", otp)

        return redirect("/verify-otp")

    return render_template("register.html")

# =========================================
# VERIFY OTP
# =========================================

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    if request.method == "POST":

        entered = request.form["otp"]

        if entered == session.get("otp"):

            data = session.get("temp_user")

            user = User(
                name=data["name"],
                email=data["email"],
                password=data["password"],
                mobile=data["mobile"],
                role=data["role"]
            )

            db.session.add(user)

            db.session.commit()

            flash("Registration Successful")

            return redirect("/login")

        else:

            flash("Invalid OTP")

    return render_template("verify_otp.html")

# =========================================
# LOGIN
# =========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            session["user"] = user.name

            session["role"] = user.role

            if user.role == "patient":
                return redirect("/patient-dashboard")

            elif user.role == "doctor":
                return redirect("/doctor-dashboard")

            else:
                return redirect("/admin-dashboard")

        else:

            flash("Invalid Login")

    return render_template("login.html")

# =========================================
# PATIENT DASHBOARD
# =========================================

@app.route("/patient-dashboard")
def patient_dashboard():

    appointments = Appointment.query.all()

    return render_template(
        "patient_dashboard.html",
        appointments=appointments
    )

# =========================================
# DOCTOR DASHBOARD
# =========================================

@app.route("/doctor-dashboard")
def doctor_dashboard():

    appointments = Appointment.query.all()

    return render_template(
        "doctor_dashboard.html",
        appointments=appointments
    )

# =========================================
# ADMIN DASHBOARD
# =========================================

@app.route("/admin-dashboard")
def admin_dashboard():

    users = User.query.all()

    appointments = Appointment.query.all()

    return render_template(
        "admin_dashboard.html",
        users=users,
        appointments=appointments
    )

# =========================================
# APPOINTMENT
# =========================================

@app.route("/appointment", methods=["GET", "POST"])
def appointment():

    if request.method == "POST":

        patient = request.form["patient"]

        doctor = request.form["doctor"]

        date = request.form["date"]

        ap = Appointment(
            patient=patient,
            doctor=doctor,
            date=date,
            status="Pending"
        )

        db.session.add(ap)

        db.session.commit()

        return redirect("/patient-dashboard")

    appointments = Appointment.query.all()

    return render_template(
        "appointment.html",
        appointments=appointments
    )

# =========================================
# CHATBOT
# =========================================

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

# =========================================
# AI PREDICTION
# =========================================

@app.route("/ai-prediction")
def ai_prediction():
    return render_template("ai_prediction.html")

# =========================================
# SEARCH
# =========================================

@app.route("/search")
def search():

    appointments = Appointment.query.all()

    return render_template(
        "search.html",
        appointments=appointments
    )

# =========================================
# LOGOUT
# =========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# =========================================
# RUN
# =========================================

if __name__ == "__main__":
    app.run(debug=True)