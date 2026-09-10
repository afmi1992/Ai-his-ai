from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from extensions import db
from models.medication import Medication
from models.prescription import Prescription
from models.dispensing import Dispensing
from models.patient import Patient
from models.doctor import Doctor
from auth.forms import PrescriptionForm, DispensingForm
from services.ai.drug_safety import evaluate_prescription_safety


def register_pharmacy_routes(app):

    @app.route("/pharmacy")
    @login_required
    def pharmacy_dashboard():

        medications_count = Medication.query.filter_by(
            is_deleted=False
        ).count()

        pending_prescriptions_count = Prescription.query.filter_by(
            is_deleted=False,
            status="Prescribed"
        ).count()

        dispensed_count = Dispensing.query.filter_by(
            is_deleted=False
        ).count()

        recent_prescriptions = Prescription.query.filter_by(
            is_deleted=False
        ).order_by(
            Prescription.prescribed_at.desc()
        ).limit(10).all()

        return render_template(
            "pharmacy.html",
            medications_count=medications_count,
            pending_prescriptions_count=pending_prescriptions_count,
            dispensed_count=dispensed_count,
            recent_prescriptions=recent_prescriptions
        )

    @app.route("/pharmacy/prescriptions/create", methods=["GET", "POST"])
    @login_required
    def create_prescription():

        form = PrescriptionForm()

        patients = Patient.query.filter_by(is_deleted=False).order_by(Patient.full_name.asc()).all()
        doctors = Doctor.query.filter_by(is_deleted=False, status="Active").order_by(Doctor.full_name.asc()).all()
        medications = Medication.query.filter_by(
            is_deleted=False,
            is_active=True
        ).order_by(Medication.medication_name.asc()).all()

        form.patient_id.choices = [
            (patient.id, f"{patient.mrn} - {patient.full_name}")
            for patient in patients
        ]

        form.doctor_id.choices = [
            (doctor.id, f"{doctor.full_name} - {doctor.specialty}")
            for doctor in doctors
        ]

        form.medication_id.choices = [
            (
                medication.id,
                f"{medication.medication_name} | {medication.strength}"
            )
            for medication in medications
        ]

        safety_alerts = None

        if form.validate_on_submit():

            selected_patient = Patient.query.get(form.patient_id.data)
            selected_med = Medication.query.get(form.medication_id.data)

            # Evaluate online FDA API & clinical contraindications
            detected_alerts = evaluate_prescription_safety(
                selected_patient,
                selected_med.medication_name
            )

            # Check whether 2-step confirmation override was submitted
            step1_confirmed = request.form.get("override_step1") == "on"
            step2_reason = (request.form.get("override_reason") or "").strip()

            # Intercept if high/lethal risk exists and override is incomplete
            if detected_alerts and not (step1_confirmed and step2_reason):
                safety_alerts = detected_alerts
                flash("Clinical Decision Support: Critical drug interaction or contraindication identified.", "danger")
                return render_template(
                    "create_prescription.html",
                    form=form,
                    safety_alerts=safety_alerts,
                    selected_medication=selected_med,
                    selected_patient=selected_patient
                )

            # Append override rationale to instructions if forced
            final_instructions = form.instructions.data or ""
            if detected_alerts and step1_confirmed and step2_reason:
                final_instructions += f"\n[AI Safety Warning Overridden by Doctor: {step2_reason}]"

            prescription = Prescription(
                patient_id=form.patient_id.data,
                doctor_id=form.doctor_id.data,
                medication_id=form.medication_id.data,
                dose=form.dose.data,
                frequency=form.frequency.data,
                duration=form.duration.data,
                instructions=final_instructions,
                status="Prescribed"
            )

            db.session.add(prescription)
            db.session.commit()

            flash("Prescription created successfully", "success")
            return redirect(url_for("pharmacy_dashboard"))

        return render_template(
            "create_prescription.html",
            form=form,
            safety_alerts=safety_alerts
        )

    @app.route("/pharmacy/prescriptions/<int:prescription_id>/dispense", methods=["GET", "POST"])
    @login_required
    def dispense_prescription(prescription_id):

        prescription = Prescription.query.get_or_404(prescription_id)
        form = DispensingForm()

        if form.validate_on_submit():

            dispensing = Dispensing(
                prescription_id=prescription.id,
                quantity_dispensed=form.quantity_dispensed.data,
                dispensed_by=form.dispensed_by.data,
                dispensing_notes=form.dispensing_notes.data
            )

            prescription.status = "Dispensed"

            db.session.add(dispensing)
            db.session.commit()

            flash("Medication dispensed successfully", "success")
            return redirect(url_for("pharmacy_dashboard"))

        return render_template(
            "create_dispensing.html",
            form=form,
            prescription=prescription
        )

    @app.route("/pharmacy/prescriptions/<int:prescription_id>/delete", methods=["POST"])
    @login_required
    def delete_prescription(prescription_id):

        prescription = Prescription.query.get_or_404(prescription_id)
        prescription.is_deleted = True
        db.session.commit()

        flash("Prescription deleted successfully.", "info")
        return redirect(url_for("pharmacy_dashboard"))