# =========================================================
# REQUIRED LIBRARIES IMPORT KARNA
# =========================================================

# Flask web application banane ke liye use hota hai
from flask import Flask, render_template, request, redirect, session, flash

# SQLAlchemy database ko Flask se connect karta hai
from flask_sqlalchemy import SQLAlchemy

# dotenv .env file se variables load karta hai
from dotenv import load_dotenv

# os system variables access karne ke liye
import os

# random OTP generate karne ke liye
import random

# =========================================================
# ENVIRONMENT VARIABLES LOAD KARNA
# =========================================================

# .env file ka data load karega
load_dotenv()

# =========================================================
# FLASK APPLICATION CREATE KARNA
# =========================================================

# Flask app object create ho raha hai
app = Flask(__name__)

# =========================================================
# SECRET KEY
# =========================================================

# Secret key session aur security ke liye use hoti hai
app.secret_key = "hdmis_secret"

# =========================================================
# DATABASE CONFIGURATION
# =========================================================

# DATABASE_URL environment variable se database URL lena
DATABASE_URL = os.getenv("DATABASE_URL")

# Agar DATABASE_URL nahi mila
# toh SQLite database use hoga
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///database.db"

# Flask ko database URI provide karna
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

# Modification tracking band karna
# performance better hoti hai
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SQLAlchemy initialize karna
db = SQLAlchemy(app)

# =========================================================
# USER TABLE
# =========================================================

# Is table me:
# Patient
# Doctor
# Admin
# ka data store hoga

class User(db.Model):

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # User ka naam
    name = db.Column(db.String(200))

    # Email unique hoga
    email = db.Column(db.String(200), unique=True)

    # Password store hoga
    password = db.Column(db.String(200))

    # Mobile number
    mobile = db.Column(db.String(20))

    # Role:
    # patient / doctor / admin
    role = db.Column(db.String(50))

# =========================================================
# APPOINTMENT TABLE
# =========================================================

# Appointment details store hongi

class Appointment(db.Model):

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Patient ka naam
    patient = db.Column(db.String(200))

    # Doctor ka naam
    doctor = db.Column(db.String(200))

    # Appointment date
    date = db.Column(db.String(100))

    # Appointment status
    # Pending / Approved / Rejected
    status = db.Column(db.String(100))

# =========================================================
# DATABASE TABLE CREATE KARNA
# =========================================================

# Automatically tables create karega
with app.app_context():
    db.create_all()

# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    # User ko login page pe bhejna
    return redirect("/login")

# =========================================================
# USER REGISTRATION
# =========================================================

# GET  -> Register page open karega
# POST -> Form submit karega

@app.route("/register", methods=["GET", "POST"])
def register():

    # Agar form submit hua hai
    if request.method == "POST":

        # Form data lena
        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]

        mobile = request.form["mobile"]

        role = request.form["role"]

        # =================================================
        # CHECK KARNA KI EMAIL PEHLE SE EXIST KARTI HAI YA NAHI
        # =================================================

        existing = User.query.filter_by(email=email).first()

        # Agar email already exist karti hai
        if existing:

            flash("Email already exists")

            return redirect("/register")

        # =================================================
        # OTP GENERATE KARNA
        # =================================================

        # Random 4-digit OTP generate hoga
        otp = random.randint(1000, 9999)

        # OTP session me save karna
        session["otp"] = str(otp)

        # Temporary user data session me store karna
        session["temp_user"] = {

            "name": name,

            "email": email,

            "password": password,

            "mobile": mobile,

            "role": role
        }

        # OTP terminal me print hoga
        print("OTP:", otp)

        # User ko OTP verification page pe bhejna
        return redirect("/verify-otp")

    # Register page open karna
    return render_template("register.html")

# =========================================================
# OTP VERIFICATION
# =========================================================

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    # Agar form submit hua
    if request.method == "POST":

        # User ka entered OTP lena
        entered = request.form["otp"]

        # =================================================
        # OTP VERIFY KARNA
        # =================================================

        # Entered OTP aur session OTP compare karna
        if entered == session.get("otp"):

            # Temporary user data lena
            data = session.get("temp_user")

            # New user object create karna
            user = User(

                name=data["name"],

                email=data["email"],

                password=data["password"],

                mobile=data["mobile"],

                role=data["role"]
            )

            # User database me add karna
            db.session.add(user)

            # Changes save karna
            db.session.commit()

            # Success message show karna
            flash("Registration Successful")

            # Login page pe redirect karna
            return redirect("/login")

        else:

            # Agar OTP galat hai
            flash("Invalid OTP")

    # OTP page open karna
    return render_template("verify_otp.html")

# =========================================================
# LOGIN SYSTEM
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # Agar login form submit hua
    if request.method == "POST":

        # Email aur password lena
        email = request.form["email"]

        password = request.form["password"]

        # =================================================
        # DATABASE ME USER CHECK KARNA
        # =================================================

        user = User.query.filter_by(

            email=email,

            password=password

        ).first()

        # =================================================
        # LOGIN SUCCESS
        # =================================================

        if user:

            # Session me user data save karna
            session["user"] = user.name

            session["role"] = user.role

            # =============================================
            # ROLE BASED LOGIN
            # =============================================

            # Patient login
            if user.role == "patient":

                return redirect("/patient-dashboard")

            # Doctor login
            elif user.role == "doctor":

                return redirect("/doctor-dashboard")

            # Admin login
            else:

                return redirect("/admin-dashboard")

        else:

            # Invalid login message
            flash("Invalid Login")

    # Login page open karna
    return render_template("login.html")

# =========================================================
# PATIENT DASHBOARD
# =========================================================

@app.route("/patient-dashboard")
def patient_dashboard():

    # Sare appointments fetch karna
    appointments = Appointment.query.all()

    # Patient dashboard open karna
    return render_template(

        "patient_dashboard.html",

        appointments=appointments
    )

# =========================================================
# DOCTOR DASHBOARD
# =========================================================

@app.route("/doctor-dashboard")
def doctor_dashboard():

    # Sare appointments fetch karna
    appointments = Appointment.query.all()

    # Doctor dashboard open karna
    return render_template(

        "doctor_dashboard.html",

        appointments=appointments
    )

# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin-dashboard")
def admin_dashboard():

    # Sare users fetch karna
    users = User.query.all()

    # Sare appointments fetch karna
    appointments = Appointment.query.all()

    # Admin dashboard open karna
    return render_template(

        "admin_dashboard.html",

        users=users,

        appointments=appointments
    )

# =========================================================
# APPOINTMENT BOOKING
# =========================================================

@app.route("/appointment", methods=["GET", "POST"])
def appointment():

    # Agar form submit hua
    if request.method == "POST":

        # Form data lena
        patient = request.form["patient"]

        doctor = request.form["doctor"]

        date = request.form["date"]

        # =================================================
        # APPOINTMENT OBJECT CREATE KARNA
        # =================================================

        ap = Appointment(

            patient=patient,

            doctor=doctor,

            date=date,

            # Default status Pending
            status="Pending"
        )

        # Appointment database me add karna
        db.session.add(ap)

        # Changes save karna
        db.session.commit()

        # Patient dashboard pe redirect karna
        return redirect("/patient-dashboard")

    # Sare appointments fetch karna
    appointments = Appointment.query.all()

    # Appointment page open karna
    return render_template(

        "appointment.html",

        appointments=appointments
    )

# =========================================================
# CHATBOT PAGE
# =========================================================

@app.route("/chatbot")
def chatbot():

    # Chatbot page open karna
    return render_template("chatbot.html")

# =========================================================
# AI PREDICTION PAGE
# =========================================================

@app.route("/ai-prediction")
def ai_prediction():

    # AI prediction page open karna
    return render_template("ai_prediction.html")

# =========================================================
# SEARCH PAGE
# =========================================================

@app.route("/search")
def search():

    # Sare appointments fetch karna
    appointments = Appointment.query.all()

    # Search page open karna
    return render_template(

        "search.html",

        appointments=appointments
    )

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    # Session data clear karna
    session.clear()

    # Login page pe bhejna
    return redirect("/login")

# =========================================================
# APPLICATION RUN KARNA
# =========================================================

if __name__ == "__main__":

    # Flask app run karega

    # debug=True ka matlab:
    # Code change hote hi server automatically restart hoga
    app.run(debug=True)