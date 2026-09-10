from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from extensions import db

from models.patient import Patient
from models.dental import DentalRecord
from models.dental_visit import DentalVisit


def register_dental_routes(app):

    # ==========================================
    # Dental Clinic - Patient Search
    # ==========================================

    @app.route("/dental")
    @login_required
    def dental_clinic():

        search = request.args.get("search", "").strip()

        query = Patient.query.filter_by(
            is_deleted=False
        )

        # Search by Patient ID or Patient Name
        if search:

            if search.isdigit():

                query = query.filter(
                    Patient.id == int(search)
                )

            else:

                query = query.filter(
                    Patient.full_name.ilike(f"%{search}%")
                )

        patients = query.order_by(
            Patient.full_name
        ).all()

        return render_template(
            "dental.html",
            patients=patients,
            search=search
        )

    # ==========================================
    # Dental Patient Profile
    # ==========================================

    @app.route("/dental/patient/<int:patient_id>")
    @login_required
    def dental_patient_profile(patient_id):

        patient = Patient.query.filter_by(
            id=patient_id,
            is_deleted=False
        ).first_or_404()

        # --------------------------------------
        # Dental Records / Tooth Chart
        # --------------------------------------

        dental_records = DentalRecord.query.filter_by(
            patient_id=patient.id
        ).order_by(
            DentalRecord.tooth_number
        ).all()

        # --------------------------------------
        # Separate Permanent / Primary Teeth
        # --------------------------------------

        permanent_records = [
            record
            for record in dental_records
            if record.dentition == "Permanent"
        ]

        primary_records = [
            record
            for record in dental_records
            if record.dentition == "Primary"
        ]

        # --------------------------------------
        # Dictionaries for easy tooth lookup
        # --------------------------------------

        permanent_teeth = {
            record.tooth_number: record
            for record in permanent_records
        }

        primary_teeth = {
            record.tooth_number: record
            for record in primary_records
        }

        # --------------------------------------
        # Dental Visit Documentation
        # --------------------------------------

        dental_visits = DentalVisit.query.filter_by(
            patient_id=patient.id
        ).order_by(
            DentalVisit.visit_date.desc()
        ).all()

        return render_template(
            "dental_patient.html",

            patient=patient,

            dental_records=dental_records,

            permanent_records=permanent_records,
            primary_records=primary_records,

            permanent_teeth=permanent_teeth,
            primary_teeth=primary_teeth,

            dental_visits=dental_visits
        )

    # ==========================================
    # Save / Update Dental Tooth Record
    # ==========================================

    @app.route(
        "/dental/patient/<int:patient_id>/tooth/save",
        methods=["POST"]
    )
    @login_required
    def save_dental_record(patient_id):

        patient = Patient.query.filter_by(
            id=patient_id,
            is_deleted=False
        ).first_or_404()

        tooth_number = request.form.get(
            "tooth_number",
            ""
        ).strip()

        dentition = request.form.get(
            "dentition",
            "Permanent"
        ).strip()

        diagnosis_code = request.form.get(
            "diagnosis_code",
            ""
        ).strip()

        notes = request.form.get(
            "notes",
            ""
        ).strip()

        # --------------------------------------
        # Validation
        # --------------------------------------

        if not tooth_number:

            flash(
                "Tooth number is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "dental_patient_profile",
                    patient_id=patient.id
                )
            )

        if dentition not in [
            "Permanent",
            "Primary"
        ]:

            flash(
                "Invalid dentition type.",
                "danger"
            )

            return redirect(
                url_for(
                    "dental_patient_profile",
                    patient_id=patient.id
                )
            )

        # --------------------------------------
        # Find existing record
        # --------------------------------------

        dental_record = DentalRecord.query.filter_by(
            patient_id=patient.id,
            tooth_number=tooth_number,
            dentition=dentition
        ).first()

        # --------------------------------------
        # Update existing record
        # --------------------------------------

        if dental_record:

            dental_record.diagnosis_code = (
                diagnosis_code or None
            )

            dental_record.notes = (
                notes or None
            )

            message = (
                f"Tooth {tooth_number} updated successfully."
            )

        # --------------------------------------
        # Create new record
        # --------------------------------------

        else:

            dental_record = DentalRecord(
                patient_id=patient.id,
                tooth_number=tooth_number,
                dentition=dentition,
                diagnosis_code=diagnosis_code or None,
                notes=notes or None
            )

            db.session.add(dental_record)

            message = (
                f"Tooth {tooth_number} added successfully."
            )

        db.session.commit()

        flash(
            message,
            "success"
        )

        return redirect(
            url_for(
                "dental_patient_profile",
                patient_id=patient.id
            )
        )

    # ==========================================
    # Delete Dental Tooth Record
    # ==========================================

    @app.route(
        "/dental/patient/<int:patient_id>/tooth/<int:record_id>/delete",
        methods=["POST"]
    )
    @login_required
    def delete_dental_record(
        patient_id,
        record_id
    ):

        patient = Patient.query.filter_by(
            id=patient_id,
            is_deleted=False
        ).first_or_404()

        dental_record = DentalRecord.query.filter_by(
            id=record_id,
            patient_id=patient.id
        ).first_or_404()

        db.session.delete(
            dental_record
        )

        db.session.commit()

        flash(
            "Dental tooth record deleted successfully.",
            "success"
        )

        return redirect(
            url_for(
                "dental_patient_profile",
                patient_id=patient.id
            )
        )

    # ==========================================
    # Add Dental Visit Documentation
    # ==========================================

    @app.route(
        "/dental/patient/<int:patient_id>/visit/save",
        methods=["POST"]
    )
    @login_required
    def save_dental_visit(patient_id):

        patient = Patient.query.filter_by(
            id=patient_id,
            is_deleted=False
        ).first_or_404()

        visit_date = request.form.get(
            "visit_date",
            ""
        ).strip()

        chief_complaint = request.form.get(
            "chief_complaint",
            ""
        ).strip()

        procedure = request.form.get(
            "procedure",
            ""
        ).strip()

        future_procedure_required = request.form.get(
            "future_procedure_required",
            ""
        ).strip()

        # --------------------------------------
        # Validation
        # --------------------------------------

        if not visit_date:

            flash(
                "Visit date is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "dental_patient_profile",
                    patient_id=patient.id
                )
            )

        # --------------------------------------
        # Convert date string to Python date
        # --------------------------------------

        from datetime import datetime

        try:

            parsed_visit_date = datetime.strptime(
                visit_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Invalid visit date.",
                "danger"
            )

            return redirect(
                url_for(
                    "dental_patient_profile",
                    patient_id=patient.id
                )
            )

        # --------------------------------------
        # Create Dental Visit
        # --------------------------------------

        dental_visit = DentalVisit(
            patient_id=patient.id,
            visit_date=parsed_visit_date,
            chief_complaint=chief_complaint or None,
            procedure=procedure or None,
            future_procedure_required=(
                future_procedure_required or None
            )
        )

        db.session.add(
            dental_visit
        )

        db.session.commit()

        flash(
            "Dental visit documented successfully.",
            "success"
        )

        return redirect(
            url_for(
                "dental_patient_profile",
                patient_id=patient.id
            )
        )

    # ==========================================
    # Delete Dental Visit
    # ==========================================

    @app.route(
        "/dental/patient/<int:patient_id>/visit/<int:visit_id>/delete",
        methods=["POST"]
    )
    @login_required
    def delete_dental_visit(
        patient_id,
        visit_id
    ):

        patient = Patient.query.filter_by(
            id=patient_id,
            is_deleted=False
        ).first_or_404()

        dental_visit = DentalVisit.query.filter_by(
            id=visit_id,
            patient_id=patient.id
        ).first_or_404()

        db.session.delete(
            dental_visit
        )

        db.session.commit()

        flash(
            "Dental visit deleted successfully.",
            "success"
        )

        return redirect(
            url_for(
                "dental_patient_profile",
                patient_id=patient.id
            )
        )