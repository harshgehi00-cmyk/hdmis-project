# =========================================================
# HDMIS PROJECT
# Health Data Management Information System
# =========================================================

# Flask ke important modules import karna
from flask import Flask, render_template, request, redirect, session, flash

# Database handle karne ke liye SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# .env file load karne ke liye
from dotenv import load_dotenv

# OS operations ke liye
import os

# OTP generate karne ke liye
import random

# OpenAI chatbot ke liye
from openai import OpenAI

# =========================================================
# ENV FILE LOAD
# =========================================================

# .env file ke variables load honge
load_dotenv()

# =========================================================
# FLASK APP INITIALIZE
# =========================================================

# Flask app create
app = Flask(__name__)

# Session aur flash messages ke liye secret key
app.secret_key = "hdmis_secret"

# =========================================================
# DATABASE CONFIGURATION
# =========================================================

# Environment variable se database URL lena
DATABASE_URL = os.getenv("DATABASE_URL")

# Agar Render/PostgreSQL available nahi hai
# to local sqlite database use hoga
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///database.db"

# Flask database config
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Database object create
db = SQLAlchemy(app)

# =========================================================
# OPENAI CONFIGURATION
# =========================================================

# OpenAI client initialize
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =========================================================
# USER TABLE
# =========================================================

class User(db.Model):

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # User ka naam
    name = db.Column(db.String(200))

    # Email unique rahega
    email = db.Column(db.String(200), unique=True)

    # Password
    password = db.Column(db.String(200))

    # Role -> Patient ya Doctor
    role = db.Column(db.String(100))

# =========================================================
# APPOINTMENT TABLE
# =========================================================

class Appointment(db.Model):

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Patient name
    patient = db.Column(db.String(200))

    # Doctor name
    doctor = db.Column(db.String(200))

    # Disease name
    disease = db.Column(db.String(200))

    # Appointment date
    date = db.Column(db.String(100))

    # Status -> Pending / Completed
    status = db.Column(db.String(100))

# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    # Home page render karega
    return render_template("index.html")

# =========================================================
# REGISTER PAGE
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    # Agar form submit hua
    if request.method == "POST":

        # Form data lena
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        # Check karo email already exist karta hai ya nahi
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:

            flash("User already exists")
            return redirect("/register")

        # Random OTP generate
        otp = random.randint(1000, 9999)

        # OTP aur temporary data session me save
        session["otp"] = str(otp)

        session["temp_name"] = name
        session["temp_email"] = email
        session["temp_password"] = password
        session["temp_role"] = role

        # Console me OTP show
        print("OTP:", otp)

        # Flash message me OTP show
        flash(f"Demo OTP: {otp}")

        # OTP verification page pe bhejo
        return redirect("/verify-otp")

    return render_template("register.html")

# =========================================================
# OTP VERIFICATION PAGE
# =========================================================

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    # Agar form submit hua
    if request.method == "POST":

        # User ka entered OTP
        user_otp = request.form["otp"]

        # OTP match hua
        if user_otp == session.get("otp"):

            # New user object create
            new_user = User(
                name=session.get("temp_name"),
                email=session.get("temp_email"),
                password=session.get("temp_password"),
                role=session.get("temp_role")
            )

            # Database me save
            db.session.add(new_user)
            db.session.commit()

            flash("Registration Successful")

            return redirect("/login")

        else:

            flash("Invalid OTP")

    return render_template("verify_otp.html")

# =========================================================
# LOGIN PAGE
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # Agar login form submit hua
    if request.method == "POST":

        # Email aur password lena
        email = request.form["email"]
        password = request.form["password"]

        # Database me user search
        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        # Agar user mil gaya
        if user:

            # Session me user info save
            session["user"] = user.name
            session["role"] = user.role

            # Doctor dashboard
            if user.role == "Doctor":
                return redirect("/doctor-dashboard")

            # Patient dashboard
            return redirect("/patient-dashboard")

        else:

            flash("Invalid Credentials")

    return render_template("login.html")

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    # Session clear
    session.clear()

    # Login page pe bhejo
    return redirect("/login")

# =========================================================
# PATIENT DASHBOARD
# =========================================================

@app.route("/patient-dashboard")
def patient_dashboard():

    # Current patient ke appointments fetch
    appointments = Appointment.query.filter_by(
        patient=session.get("user")
    ).all()

    # Total appointments
    total = len(appointments)

    # Completed appointments count
    completed = len([
        appt for appt in appointments
        if appt.status == "Completed"
    ])

    # Pending appointments count
    pending = len([
        appt for appt in appointments
        if appt.status == "Pending"
    ])

    return render_template(
        "patient_dashboard.html",
        appointments=appointments,
        total=total,
        completed=completed,
        pending=pending
    )

# =========================================================
# DOCTOR DASHBOARD
# =========================================================

@app.route("/doctor-dashboard")
def doctor_dashboard():

    # Sab appointments fetch
    appointments = Appointment.query.all()

    # Total appointments
    total = len(appointments)

    return render_template(
        "doctor_dashboard.html",
        appointments=appointments,
        total=total
    )

# =========================================================
# BOOK APPOINTMENT
# =========================================================

@app.route("/appointment", methods=["GET", "POST"])
def appointment():

    # Form submit hone pe
    if request.method == "POST":

        # Form data lena
        patient = request.form["patient"]
        doctor = request.form["doctor"]
        disease = request.form["disease"]
        date = request.form["date"]

        # New appointment object
        new_appointment = Appointment(
            patient=patient,
            doctor=doctor,
            disease=disease,
            date=date,
            status="Pending"
        )

        # Database me save
        db.session.add(new_appointment)
        db.session.commit()

        flash("Appointment Booked Successfully")

        return redirect("/patient-dashboard")

    return render_template("appointment.html")

# =========================================================
# SEARCH PATIENT
# =========================================================

@app.route("/search", methods=["GET", "POST"])
def search():

    appointments = []

    # Search form submit hua
    if request.method == "POST":

        # Patient name lena
        patient_name = request.form["patient"]

        # Database search
        appointments = Appointment.query.filter(
            Appointment.patient.like(f"%{patient_name}%")
        ).all()

    return render_template(
        "search.html",
        appointments=appointments
    )

# =========================================================
# MEDICAL HISTORY
# =========================================================

@app.route("/history")
def history():

    # Current user ka medical history
    appointments = Appointment.query.filter_by(
        patient=session.get("user")
    ).all()

    return render_template(
        "history.html",
        appointments=appointments
    )

# =========================================================
# REPORTS PAGE
# =========================================================

@app.route("/reports")
def reports():

    # All appointments fetch
    appointments = Appointment.query.all()

    return render_template(
        "reports.html",
        appointments=appointments
    )

# =========================================================
# AI CHATBOT
# =========================================================

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():

    # Default response blank
    response = ""

    # Form submit hone pe
    if request.method == "POST":

        # User question lena
        question = request.form["question"]

        try:

            # OpenAI API call
            ai_response = client.chat.completions.create(

                model="gpt-3.5-turbo",

                messages=[
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )

            # AI response extract
            response = ai_response.choices[0].message.content

        except Exception as e:

            # Error show
            response = str(e)

    return render_template(
        "chatbot.html",
        response=response
    )

# =========================================================
# AI PREDICTION PAGE
# =========================================================

@app.route("/prediction")
def prediction():

    return render_template("prediction.html")

# =========================================================
# DATABASE CREATE
# =========================================================

# Agar tables exist nahi karti to create karo
with app.app_context():

    db.create_all()

# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    # Flask app run
    app.run(debug=True)