from datetime import datetime

from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.lab_order import LabOrder
from models.lab_test import LabTest
from models.lab_result import LabResult
from models.patient import Patient
from models.doctor import Doctor
from auth.forms import LabOrderForm, LabResultForm


def register_laboratory_routes(app):

    @app.route("/laboratory")
    @login_required
    def laboratory():

        lab_tests_count = LabTest.query.filter_by(
            is_deleted=False
        ).count()

        pending_orders_count = LabOrder.query.filter_by(
            is_deleted=False,
            status="Ordered"
        ).count()

        completed_results_count = LabResult.query.filter_by(
            is_deleted=False
        ).count()

        recent_orders = LabOrder.query.filter_by(
            is_deleted=False
        ).order_by(
            LabOrder.ordered_at.desc()
        ).limit(10).all()

        return render_template(
            "laboratory.html",
            lab_tests_count=lab_tests_count,
            pending_orders_count=pending_orders_count,
            completed_results_count=completed_results_count,
            recent_orders=recent_orders
        )

    @app.route("/laboratory/orders/create", methods=["GET", "POST"])
    @login_required
    def create_lab_order():

        form = LabOrderForm()

        patients = Patient.query.filter_by(is_deleted=False).all()
        doctors = Doctor.query.filter_by(is_deleted=False, status="Active").all()
        lab_tests = LabTest.query.filter_by(is_deleted=False, is_active=True).all()

        form.patient_id.choices = [
            (patient.id, f"{patient.mrn} - {patient.full_name}")
            for patient in patients
        ]

        form.doctor_id.choices = [
            (doctor.id, f"{doctor.full_name} - {doctor.specialty}")
            for doctor in doctors
        ]

        form.lab_test_id.choices = [
            (test.id, f"{test.test_code} - {test.test_name}")
            for test in lab_tests
        ]

        if form.validate_on_submit():

            lab_order = LabOrder(
                patient_id=form.patient_id.data,
                doctor_id=form.doctor_id.data,
                lab_test_id=form.lab_test_id.data,
                priority=form.priority.data,
                clinical_notes=form.clinical_notes.data,
                status="Ordered"
            )

            db.session.add(lab_order)
            db.session.commit()

            flash("Lab order created successfully", "success")
            return redirect(url_for("laboratory"))

        return render_template(
            "create_lab_order.html",
            form=form
        )

    @app.route("/laboratory/orders/<int:order_id>/result/create", methods=["GET", "POST"])
    @login_required
    def create_lab_result(order_id):

        lab_order = LabOrder.query.get_or_404(order_id)
        form = LabResultForm()

        if form.validate_on_submit():

            lab_result = LabResult(
                lab_order_id=lab_order.id,
                result_value=form.result_value.data,
                result_unit=form.result_unit.data,
                reference_range=form.reference_range.data,
                flag=form.flag.data,
                interpretation=form.interpretation.data,
                validated_by=form.validated_by.data,
                validated_at=datetime.utcnow()
            )

            lab_order.status = "Completed"

            db.session.add(lab_result)
            db.session.commit()

            flash("Lab result saved successfully", "success")
            return redirect(url_for("laboratory"))

        form.result_unit.data = lab_order.lab_test.unit
        form.reference_range.data = lab_order.lab_test.reference_range

        return render_template(
            "create_lab_result.html",
            form=form,
            lab_order=lab_order
        )