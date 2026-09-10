from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    TextAreaField,
    DateField,
    TimeField,
    IntegerField
)

from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional
)


class LoginForm(FlaskForm):

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Login")


class CreateUserForm(FlaskForm):

    full_name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=3, max=150)]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8)]
    )

    role_id = SelectField(
        "Role",
        coerce=int,
        validators=[DataRequired()]
    )

    submit = SubmitField("Create User")


class EditUserForm(FlaskForm):

    full_name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=3, max=150)]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    role_id = SelectField(
        "Role",
        coerce=int,
        validators=[DataRequired()]
    )

    submit = SubmitField("Update User")


class PatientForm(FlaskForm):

    mrn = StringField(
        "MRN",
        validators=[DataRequired(), Length(min=3, max=50)]
    )

    full_name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=3, max=200)]
    )

    gender = SelectField(
        "Gender",
        choices=[
            ("Male", "Male"),
            ("Female", "Female")
        ],
        validators=[DataRequired()]
    )

    phone = StringField(
        "Phone",
        validators=[DataRequired(), Length(min=5, max=50)]
    )

    blood_group = SelectField(
        "Blood Group",
        choices=[
            ("A+", "A+"),
            ("A-", "A-"),
            ("B+", "B+"),
            ("B-", "B-"),
            ("AB+", "AB+"),
            ("AB-", "AB-"),
            ("O+", "O+"),
            ("O-", "O-")
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField("Save Patient")


class AppointmentForm(FlaskForm):

    patient_id = SelectField(
        "Patient",
        coerce=int,
        validators=[DataRequired()]
    )

    doctor_id = SelectField(
        "Doctor",
        coerce=int,
        validators=[DataRequired()]
    )

    appointment_date = DateField(
        "Appointment Date",
        validators=[DataRequired()]
    )

    appointment_time = TimeField(
        "Appointment Time",
        validators=[DataRequired()]
    )

    appointment_type = SelectField(
        "Appointment Type",
        choices=[
            ("In-Person", "In-Person"),
            ("Telemedicine", "Telemedicine")
        ]
    )

    status = SelectField(
        "Status",
        choices=[
            ("Scheduled", "Scheduled"),
            ("Confirmed", "Confirmed"),
            ("Completed", "Completed"),
            ("Cancelled", "Cancelled")
        ]
    )

    reason = TextAreaField("Reason")

    notes = TextAreaField("Notes")

    telemedicine_link = StringField(
        "Telemedicine Link"
    )

    submit = SubmitField("Save Appointment")


class DoctorForm(FlaskForm):

    employee_id = StringField(
        "Employee ID",
        validators=[DataRequired(), Length(min=2, max=50)]
    )

    full_name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=3, max=200)]
    )

    specialty = StringField(
        "Specialty",
        validators=[DataRequired(), Length(min=3, max=150)]
    )

    department = StringField(
        "Department",
        validators=[Length(max=150)]
    )

    phone = StringField(
        "Phone",
        validators=[Length(max=50)]
    )

    email = StringField(
        "Email",
        validators=[Email()]
    )

    license_number = StringField(
        "License Number",
        validators=[Length(max=100)]
    )

    telemedicine_enabled = SelectField(
        "Telemedicine Enabled",
        choices=[
            ("Yes", "Yes"),
            ("No", "No")
        ],
        validators=[DataRequired()]
    )

    status = SelectField(
        "Status",
        choices=[
            ("Active", "Active"),
            ("Inactive", "Inactive")
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField("Save Doctor")


class LabOrderForm(FlaskForm):

    patient_id = SelectField(
        "Patient",
        coerce=int,
        validators=[DataRequired()]
    )

    doctor_id = SelectField(
        "Doctor",
        coerce=int,
        validators=[DataRequired()]
    )

    lab_test_id = SelectField(
        "Lab Test",
        coerce=int,
        validators=[DataRequired()]
    )

    priority = SelectField(
        "Priority",
        choices=[
            ("Routine", "Routine"),
            ("Urgent", "Urgent"),
            ("STAT", "STAT")
        ],
        validators=[DataRequired()]
    )

    clinical_notes = TextAreaField(
        "Clinical Notes"
    )

    submit = SubmitField("Create Lab Order")


class LabResultForm(FlaskForm):

    result_value = StringField(
        "Result Value",
        validators=[DataRequired()]
    )

    result_unit = StringField(
        "Result Unit"
    )

    reference_range = StringField(
        "Reference Range"
    )

    flag = SelectField(
        "Flag",
        choices=[
            ("Normal", "Normal"),
            ("Low", "Low"),
            ("High", "High"),
            ("Critical", "Critical")
        ],
        validators=[DataRequired()]
    )

    interpretation = TextAreaField(
        "Interpretation"
    )

    validated_by = StringField(
        "Validated By"
    )

    submit = SubmitField("Save Result")


class RadiologyOrderForm(FlaskForm):

    patient_id = SelectField(
        "Patient",
        coerce=int,
        validators=[DataRequired()]
    )

    doctor_id = SelectField(
        "Doctor",
        coerce=int,
        validators=[DataRequired()]
    )

    radiology_test_id = SelectField(
        "Radiology Study",
        coerce=int,
        validators=[DataRequired()]
    )

    priority = SelectField(
        "Priority",
        choices=[
            ("Routine", "Routine"),
            ("Urgent", "Urgent"),
            ("STAT", "STAT")
        ],
        validators=[DataRequired()]
    )

    clinical_indication = TextAreaField(
        "Clinical Indication"
    )

    submit = SubmitField("Create Radiology Order")


class RadiologyReportForm(FlaskForm):

    findings = TextAreaField(
        "Findings",
        validators=[DataRequired()]
    )

    impression = TextAreaField(
        "Impression",
        validators=[DataRequired()]
    )

    report_status = SelectField(
        "Report Status",
        choices=[
            ("Preliminary", "Preliminary"),
            ("Final", "Final"),
            ("Amended", "Amended")
        ],
        validators=[DataRequired()]
    )

    reported_by = StringField(
        "Reported By"
    )

    submit = SubmitField("Save Radiology Report")


class PrescriptionForm(FlaskForm):

    patient_id = SelectField(
        "Patient",
        coerce=int,
        validators=[DataRequired()]
    )

    doctor_id = SelectField(
        "Doctor",
        coerce=int,
        validators=[DataRequired()]
    )

    medication_id = SelectField(
        "Medication",
        coerce=int,
        validators=[DataRequired()]
    )

    dose = StringField(
        "Dose",
        validators=[DataRequired()]
    )

    frequency = StringField(
        "Frequency",
        validators=[DataRequired()]
    )

    duration = StringField(
        "Duration",
        validators=[DataRequired()]
    )

    instructions = TextAreaField(
        "Instructions"
    )

    submit = SubmitField("Create Prescription")


class DispensingForm(FlaskForm):

    quantity_dispensed = IntegerField(
        "Quantity Dispensed",
        validators=[DataRequired()]
    )

    dispensed_by = StringField(
        "Dispensed By"
    )

    dispensing_notes = TextAreaField(
        "Dispensing Notes"
    )

    submit = SubmitField("Confirm Dispensing")


class ClinicalNoteForm(FlaskForm):

    patient_id = SelectField(
        "Patient",
        coerce=int,
        validators=[DataRequired()]
    )

    doctor_id = SelectField(
        "Doctor",
        coerce=int,
        validators=[DataRequired()]
    )

    note_type = SelectField(
        "Note Type",
        choices=[
            ("Progress Note", "Progress Note"),
            ("Initial Assessment", "Initial Assessment"),
            ("Follow-up Note", "Follow-up Note"),
            ("Discharge Note", "Discharge Note")
        ],
        validators=[DataRequired()]
    )

    chief_complaint = TextAreaField(
        "Chief Complaint",
        validators=[DataRequired()]
    )

    history_of_present_illness = TextAreaField(
        "History of Present Illness"
    )

    assessment = TextAreaField(
        "Assessment",
        validators=[DataRequired()]
    )

    plan = TextAreaField(
        "Plan",
        validators=[DataRequired()]
    )

    diagnosis_text = StringField(
        "Diagnosis"
    )

    submit = SubmitField("Save Clinical Note")


class ProblemForm(FlaskForm):

    patient_id = SelectField(
        "Patient",
        coerce=int,
        validators=[DataRequired()]
    )

    doctor_id = SelectField(
        "Doctor",
        coerce=int,
        validators=[DataRequired()]
    )

    diagnosis_name = StringField(
        "Diagnosis / Problem Name",
        validators=[DataRequired()]
    )

    icd10_code = StringField(
        "ICD-10 Code"
    )

    problem_type = SelectField(
        "Problem Type",
        choices=[
            ("Diagnosis", "Diagnosis"),
            ("Chronic Disease", "Chronic Disease"),
            ("Acute Problem", "Acute Problem"),
            ("Surgical History", "Surgical History"),
            ("Risk Factor", "Risk Factor")
        ],
        validators=[DataRequired()]
    )

    clinical_status = SelectField(
        "Clinical Status",
        choices=[
            ("Active", "Active"),
            ("Resolved", "Resolved"),
            ("Inactive", "Inactive")
        ],
        validators=[DataRequired()]
    )

    severity = SelectField(
        "Severity",
        choices=[
            ("Mild", "Mild"),
            ("Moderate", "Moderate"),
            ("Severe", "Severe"),
            ("Critical", "Critical")
        ],
        validators=[Optional()]
    )

    onset_date = DateField(
        "Onset Date",
        validators=[Optional()],
        format="%Y-%m-%d"
    )

    resolved_date = DateField(
        "Resolved Date",
        validators=[Optional()],
        format="%Y-%m-%d"
    )

    notes = TextAreaField(
        "Clinical Notes"
    )

    submit = SubmitField("Save Problem")