from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.doctor import Doctor
from auth.forms import DoctorForm


def register_doctor_routes(app):

    @app.route("/doctors")
    @login_required
    def doctors():

        doctors_list = Doctor.query.filter_by(is_deleted=False).all()

        return render_template(
            "doctors.html",
            doctors=doctors_list
        )

    @app.route("/doctors/create", methods=["GET", "POST"])
    @login_required
    def create_doctor():

        form = DoctorForm()

        if form.validate_on_submit():

            existing_doctor = Doctor.query.filter_by(
                employee_id=form.employee_id.data
            ).first()

            if existing_doctor:
                flash("Employee ID already exists", "danger")
                return redirect(url_for("create_doctor"))

            doctor = Doctor(
                employee_id=form.employee_id.data,
                full_name=form.full_name.data,
                specialty=form.specialty.data,
                department=form.department.data,
                phone=form.phone.data,
                email=form.email.data,
                license_number=form.license_number.data,
                telemedicine_enabled=True if form.telemedicine_enabled.data == "Yes" else False,
                status=form.status.data
            )

            db.session.add(doctor)
            db.session.commit()

            flash("Doctor created successfully", "success")
            return redirect(url_for("doctors"))

        return render_template("create_doctor.html", form=form)

    @app.route("/doctors/<int:doctor_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_doctor(doctor_id):

        doctor = Doctor.query.get_or_404(doctor_id)

        form = DoctorForm()

        if form.validate_on_submit():

            doctor.employee_id = form.employee_id.data
            doctor.full_name = form.full_name.data
            doctor.specialty = form.specialty.data
            doctor.department = form.department.data
            doctor.phone = form.phone.data
            doctor.email = form.email.data
            doctor.license_number = form.license_number.data
            doctor.telemedicine_enabled = True if form.telemedicine_enabled.data == "Yes" else False
            doctor.status = form.status.data

            db.session.commit()

            flash("Doctor updated successfully", "success")
            return redirect(url_for("doctors"))

        form.employee_id.data = doctor.employee_id
        form.full_name.data = doctor.full_name
        form.specialty.data = doctor.specialty
        form.department.data = doctor.department
        form.phone.data = doctor.phone
        form.email.data = doctor.email
        form.license_number.data = doctor.license_number
        form.telemedicine_enabled.data = "Yes" if doctor.telemedicine_enabled else "No"
        form.status.data = doctor.status

        return render_template(
            "edit_doctor.html",
            form=form,
            doctor=doctor
        )

    @app.route("/doctors/<int:doctor_id>/delete")
    @login_required
    def delete_doctor(doctor_id):

        doctor = Doctor.query.get_or_404(doctor_id)

        doctor.is_deleted = True
        db.session.commit()

        flash("Doctor deleted successfully", "success")
        return redirect(url_for("doctors"))