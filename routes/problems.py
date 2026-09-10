from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from extensions import db

from models.patient import Patient
from models.doctor import Doctor
from models.problem import Problem

from auth.forms import ProblemForm


def register_problem_routes(app):

    @app.route("/problems/create", methods=["GET", "POST"])
    @login_required
    def create_problem():

        form = ProblemForm()

        form.patient_id.choices = [
            (p.id, f"{p.mrn} - {p.full_name}")
            for p in Patient.query.filter_by(is_deleted=False).all()
        ]

        form.doctor_id.choices = [
            (d.id, d.full_name)
            for d in Doctor.query.filter_by(is_deleted=False).all()
        ]

        if form.validate_on_submit():

            problem = Problem(
                patient_id=form.patient_id.data,
                doctor_id=form.doctor_id.data,
                diagnosis_name=form.diagnosis_name.data,
                icd10_code=form.icd10_code.data,
                problem_type=form.problem_type.data,
                clinical_status=form.clinical_status.data,
                severity=form.severity.data,
                onset_date=form.onset_date.data,
                resolved_date=form.resolved_date.data,
                notes=form.notes.data
            )

            db.session.add(problem)
            db.session.commit()

            flash(
                "Problem saved successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "patient_profile",
                    patient_id=form.patient_id.data
                )
            )

        return render_template(
            "create_problem.html",
            form=form
        )

    @app.route("/problems/<int:problem_id>/delete", methods=["POST"])
    @login_required
    def delete_problem(problem_id):

        problem = Problem.query.get_or_404(problem_id)
        patient_id = problem.patient_id

        # Soft delete
        problem.is_deleted = True
        db.session.commit()

        flash("Problem removed successfully.", "info")

        return redirect(
            url_for(
                "patient_profile",
                patient_id=patient_id
            )
        )