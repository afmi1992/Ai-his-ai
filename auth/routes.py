from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from auth.forms import LoginForm
from models.user import User
from models.patient import Patient
from models.doctor import Doctor
from models.appointment import Appointment


def register_auth_routes(app):

    @app.route("/login", methods=["GET", "POST"])
    def login():
        print("LOGIN ROUTE HIT")
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        form = LoginForm()

        if request.method == "POST":

            email = request.form.get("email")
            password = request.form.get("password")

            user = User.query.filter_by(email=email).first()

            print("EMAIL:", email)
            print("USER:", user)
            print("PASSWORD CHECK:", user.check_password(password) if user else None)

            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("dashboard"))

            flash("Invalid email or password", "danger")

        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():

        total_patients = Patient.query.filter_by(is_deleted=False).count()
        total_doctors = Doctor.query.filter_by(is_deleted=False).count()
        total_appointments = Appointment.query.filter_by(is_deleted=False).count()

        cancelled_appointments = Appointment.query.filter_by(
            is_deleted=False,
            status="Cancelled"
        ).count()

        telemedicine_visits = Appointment.query.filter_by(
            is_deleted=False,
            is_telemedicine=True
        ).count()

        recent_appointments = Appointment.query.filter_by(
            is_deleted=False
        ).order_by(
            Appointment.created_at.desc()
        ).limit(5).all()

        recent_patients = Patient.query.filter_by(
            is_deleted=False
        ).order_by(
            Patient.created_at.desc()
        ).limit(5).all()

        from datetime import date

        today_appointments = Appointment.query.filter_by(
            is_deleted=False,
            appointment_date=date.today()
        ).order_by(
            Appointment.appointment_time
        ).all()

        return render_template(
            "dashboard.html",
            total_patients=total_patients,
            total_doctors=total_doctors,
            total_appointments=total_appointments,
            cancelled_appointments=cancelled_appointments,
            telemedicine_visits=telemedicine_visits,
            recent_appointments=recent_appointments,
            recent_patients=recent_patients,
            today_appointments=today_appointments
        )