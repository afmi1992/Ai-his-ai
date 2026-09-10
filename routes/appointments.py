from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.appointment import Appointment
from models.patient import Patient
from models.doctor import Doctor
from auth.forms import AppointmentForm


def register_appointment_routes(app):

    @app.route("/appointments")
    @login_required
    def appointments():
        appointments_list = Appointment.query.filter_by(
            is_deleted=False
        ).order_by(
            Appointment.appointment_date,
            Appointment.appointment_time
        ).all()

        return render_template(
            "appointments.html",
            appointments=appointments_list
        )

    @app.route("/appointments/calendar")
    @login_required
    def appointments_calendar():
        appointments_list = Appointment.query.filter_by(
            is_deleted=False
        ).order_by(
            Appointment.appointment_date,
            Appointment.appointment_time
        ).all()

        return render_template(
            "appointments_calendar.html",
            appointments=appointments_list
        )

    @app.route("/appointments/create", methods=["GET", "POST"])
    @login_required
    def create_appointment():

        form = AppointmentForm()

        patients = Patient.query.filter_by(is_deleted=False).all()
        doctors = Doctor.query.filter_by(
            is_deleted=False,
            status="Active"
        ).all()

        form.patient_id.choices = [
            (p.id, f"{p.mrn} - {p.full_name}") for p in patients
        ]

        form.doctor_id.choices = [
            (d.id, f"{d.full_name} - {d.specialty}") for d in doctors
        ]

        if form.validate_on_submit():

            is_telemedicine = form.appointment_type.data == "Telemedicine"

            appointment = Appointment(
                patient_id=form.patient_id.data,
                doctor_id=form.doctor_id.data,
                appointment_date=form.appointment_date.data,
                appointment_time=form.appointment_time.data,
                appointment_type=form.appointment_type.data,
                status=form.status.data,
                reason=form.reason.data,
                notes=form.notes.data,
                is_telemedicine=is_telemedicine,
                telemedicine_link=form.telemedicine_link.data if is_telemedicine else None
            )

            db.session.add(appointment)
            db.session.commit()

            flash("Appointment created successfully", "success")
            return redirect(url_for("appointments"))

        return render_template(
            "create_appointment.html",
            form=form
        )

    @app.route("/appointments/<int:appointment_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_appointment(appointment_id):

        appointment = Appointment.query.get_or_404(appointment_id)
        form = AppointmentForm()

        patients = Patient.query.filter_by(is_deleted=False).all()
        doctors = Doctor.query.filter_by(
            is_deleted=False,
            status="Active"
        ).all()

        form.patient_id.choices = [
            (p.id, f"{p.mrn} - {p.full_name}") for p in patients
        ]

        form.doctor_id.choices = [
            (d.id, f"{d.full_name} - {d.specialty}") for d in doctors
        ]

        if form.validate_on_submit():

            is_telemedicine = form.appointment_type.data == "Telemedicine"

            appointment.patient_id = form.patient_id.data
            appointment.doctor_id = form.doctor_id.data
            appointment.appointment_date = form.appointment_date.data
            appointment.appointment_time = form.appointment_time.data
            appointment.appointment_type = form.appointment_type.data
            appointment.status = form.status.data
            appointment.reason = form.reason.data
            appointment.notes = form.notes.data
            appointment.is_telemedicine = is_telemedicine
            appointment.telemedicine_link = (
                form.telemedicine_link.data if is_telemedicine else None
            )

            db.session.commit()

            flash("Appointment updated successfully", "success")
            return redirect(url_for("appointments"))

        form.patient_id.data = appointment.patient_id
        form.doctor_id.data = appointment.doctor_id
        form.appointment_date.data = appointment.appointment_date
        form.appointment_time.data = appointment.appointment_time
        form.appointment_type.data = appointment.appointment_type
        form.status.data = appointment.status
        form.reason.data = appointment.reason
        form.notes.data = appointment.notes
        form.telemedicine_link.data = appointment.telemedicine_link

        return render_template(
            "edit_appointment.html",
            form=form,
            appointment=appointment
        )

    @app.route("/appointments/<int:appointment_id>/cancel")
    @login_required
    def cancel_appointment(appointment_id):

        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.status = "Cancelled"

        db.session.commit()

        flash("Appointment cancelled successfully", "success")
        return redirect(url_for("appointments"))