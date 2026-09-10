from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.clinical_note import ClinicalNote
from models.patient import Patient
from models.doctor import Doctor
from auth.forms import ClinicalNoteForm


def register_emr_routes(app):

    @app.route("/emr/clinical-notes/create", methods=["GET", "POST"])
    @login_required
    def create_clinical_note():

        form = ClinicalNoteForm()

        patients = Patient.query.filter_by(is_deleted=False).all()
        doctors = Doctor.query.filter_by(is_deleted=False, status="Active").all()

        form.patient_id.choices = [
            (patient.id, f"{patient.mrn} - {patient.full_name}")
            for patient in patients
        ]

        form.doctor_id.choices = [
            (doctor.id, f"{doctor.full_name} - {doctor.specialty}")
            for doctor in doctors
        ]

        if form.validate_on_submit():

            clinical_note = ClinicalNote(
                patient_id=form.patient_id.data,
                doctor_id=form.doctor_id.data,
                note_type=form.note_type.data,
                chief_complaint=form.chief_complaint.data,
                history_of_present_illness=form.history_of_present_illness.data,
                assessment=form.assessment.data,
                plan=form.plan.data,
                diagnosis_text=form.diagnosis_text.data
            )

            db.session.add(clinical_note)
            db.session.commit()

            flash("Clinical note saved successfully", "success")
            return redirect(url_for("patient_profile", patient_id=clinical_note.patient_id))

        return render_template(
            "create_clinical_note.html",
            form=form
        )