from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.patient import Patient
from models.lab_order import LabOrder
from models.radiology_order import RadiologyOrder
from models.appointment import Appointment
from models.prescription import Prescription
from models.clinical_note import ClinicalNote
from models.problem import Problem
from auth.forms import PatientForm


def register_patient_routes(app):

    @app.route("/patients")
    @login_required
    def patients():

        patients_list = Patient.query.filter_by(is_deleted=False).all()

        return render_template(
            "patients.html",
            patients=patients_list
        )

    @app.route("/patients/create", methods=["GET", "POST"])
    @login_required
    def create_patient():

        form = PatientForm()

        if form.validate_on_submit():

            existing_patient = Patient.query.filter_by(
                mrn=form.mrn.data
            ).first()

            if existing_patient:
                flash("MRN already exists", "danger")
                return redirect(url_for("create_patient"))

            patient = Patient(
                mrn=form.mrn.data,
                full_name=form.full_name.data,
                gender=form.gender.data,
                phone=form.phone.data,
                blood_group=form.blood_group.data
            )

            db.session.add(patient)
            db.session.commit()

            flash("Patient created successfully", "success")
            return redirect(url_for("patients"))

        return render_template("create_patient.html", form=form)

    @app.route("/patients/<int:patient_id>")
    @login_required
    def patient_profile(patient_id):

        patient = Patient.query.get_or_404(patient_id)

        appointments = Appointment.query.filter_by(
            patient_id=patient.id,
            is_deleted=False
        ).order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc()
        ).all()

        lab_orders = LabOrder.query.filter_by(
            patient_id=patient.id,
            is_deleted=False
        ).order_by(
            LabOrder.ordered_at.desc()
        ).all()

        radiology_orders = RadiologyOrder.query.filter_by(
            patient_id=patient.id,
            is_deleted=False
        ).order_by(
            RadiologyOrder.ordered_at.desc()
        ).all()

        prescriptions = Prescription.query.filter_by(
            patient_id=patient.id,
            is_deleted=False
        ).order_by(
            Prescription.prescribed_at.desc()
        ).all()

        clinical_notes = ClinicalNote.query.filter_by(
            patient_id=patient.id,
            is_deleted=False
        ).order_by(
            ClinicalNote.created_at.desc()
        ).all()

        problems = Problem.query.filter_by(
            patient_id=patient.id,
            is_deleted=False
        ).order_by(
            Problem.created_at.desc()
        ).all()

        return render_template(
            "patient_profile.html",
            patient=patient,
            appointments=appointments,
            lab_orders=lab_orders,
            radiology_orders=radiology_orders,
            prescriptions=prescriptions,
            clinical_notes=clinical_notes,
            problems=problems
        )

    @app.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_patient(patient_id):

        patient = Patient.query.get_or_404(patient_id)
        form = PatientForm()

        if form.validate_on_submit():

            existing_patient = Patient.query.filter(
                Patient.mrn == form.mrn.data,
                Patient.id != patient.id
            ).first()

            if existing_patient:
                flash("MRN already exists", "danger")
                return redirect(url_for("edit_patient", patient_id=patient.id))

            patient.mrn = form.mrn.data
            patient.full_name = form.full_name.data
            patient.gender = form.gender.data
            patient.phone = form.phone.data
            patient.blood_group = form.blood_group.data

            db.session.commit()

            flash("Patient updated successfully", "success")
            return redirect(url_for("patients"))

        form.mrn.data = patient.mrn
        form.full_name.data = patient.full_name
        form.gender.data = patient.gender
        form.phone.data = patient.phone
        form.blood_group.data = patient.blood_group

        return render_template(
            "edit_patient.html",
            form=form,
            patient=patient
        )

    @app.route("/patients/<int:patient_id>/delete")
    @login_required
    def delete_patient(patient_id):

        patient = Patient.query.get_or_404(patient_id)

        patient.is_deleted = True
        db.session.commit()

        flash("Patient deleted successfully", "success")

        return redirect(url_for("patients"))