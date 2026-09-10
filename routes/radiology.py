from datetime import datetime

from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.radiology_test import RadiologyTest
from models.radiology_order import RadiologyOrder
from models.radiology_report import RadiologyReport
from models.patient import Patient
from models.doctor import Doctor
from auth.forms import RadiologyOrderForm, RadiologyReportForm


def register_radiology_routes(app):

    @app.route("/radiology")
    @login_required
    def radiology_dashboard():

        radiology_tests_count = RadiologyTest.query.filter_by(
            is_deleted=False
        ).count()

        pending_orders_count = RadiologyOrder.query.filter_by(
            status="Ordered",
            is_deleted=False
        ).count()

        completed_reports_count = RadiologyReport.query.filter_by(
            is_deleted=False
        ).count()

        recent_orders = RadiologyOrder.query.filter_by(
            is_deleted=False
        ).order_by(
            RadiologyOrder.ordered_at.desc()
        ).limit(10).all()

        return render_template(
            "radiology.html",
            radiology_tests_count=radiology_tests_count,
            pending_orders_count=pending_orders_count,
            completed_reports_count=completed_reports_count,
            recent_orders=recent_orders
        )

    @app.route("/radiology/orders/create", methods=["GET", "POST"])
    @login_required
    def create_radiology_order():

        form = RadiologyOrderForm()

        patients = Patient.query.filter_by(is_deleted=False).all()
        doctors = Doctor.query.filter_by(is_deleted=False, status="Active").all()

        radiology_tests = RadiologyTest.query.filter_by(
            is_deleted=False,
            is_active=True
        ).all()

        form.patient_id.choices = [
            (patient.id, f"{patient.mrn} - {patient.full_name}")
            for patient in patients
        ]

        form.doctor_id.choices = [
            (doctor.id, f"{doctor.full_name} - {doctor.specialty}")
            for doctor in doctors
        ]

        form.radiology_test_id.choices = [
            (test.id, f"{test.test_code} - {test.test_name} ({test.modality})")
            for test in radiology_tests
        ]

        if form.validate_on_submit():

            radiology_order = RadiologyOrder(
                patient_id=form.patient_id.data,
                doctor_id=form.doctor_id.data,
                radiology_test_id=form.radiology_test_id.data,
                priority=form.priority.data,
                clinical_indication=form.clinical_indication.data,
                status="Ordered"
            )

            db.session.add(radiology_order)
            db.session.commit()

            flash("Radiology order created successfully", "success")
            return redirect(url_for("radiology_dashboard"))

        return render_template(
            "create_radiology_order.html",
            form=form
        )

    @app.route("/radiology/reports/create/<int:order_id>", methods=["GET", "POST"])
    @login_required
    def create_radiology_report(order_id):

        order = RadiologyOrder.query.get_or_404(order_id)

        form = RadiologyReportForm()

        if form.validate_on_submit():

            report = RadiologyReport(
                radiology_order_id=order.id,
                findings=form.findings.data,
                impression=form.impression.data,
                report_status=form.report_status.data,
                reported_by=form.reported_by.data,
                reported_at=datetime.utcnow()
            )

            db.session.add(report)

            order.status = "Completed"

            db.session.commit()

            flash("Radiology report saved successfully", "success")
            return redirect(url_for("radiology_dashboard"))

        return render_template(
            "create_radiology_report.html",
            form=form,
            order=order
        )