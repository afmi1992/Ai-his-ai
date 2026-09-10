import os
from google import genai
from flask import redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models.patient import Patient, AILabRecord
from models.lab_order import LabOrder
from models.problem import Problem
from models.clinical_note import ClinicalNote

def register_lab_ai_routes(app):
    
    @app.route('/patient/<int:patient_id>/run_ai_review', methods=['POST'])
    @login_required
    def run_ai_review(patient_id):
        patient = Patient.query.get_or_404(patient_id)
        
        # 1. Automatically gather Lab History
        lab_orders = LabOrder.query.filter_by(patient_id=patient.id).all()
        lab_lines = []
        for order in lab_orders:
            test_name = order.lab_test.test_name if order.lab_test else "Unknown Test"
            for res in order.results:
                lab_lines.append(f"- {test_name}: {res.result_value} {res.result_unit or ''} (Flag: {res.flag})")
        raw_labs_text = "\n".join(lab_lines) if lab_lines else "No lab results recorded."

        # 2. Automatically gather Problem List
        problems = Problem.query.filter_by(patient_id=patient.id, is_deleted=False).all()
        problems_text = ", ".join([p.diagnosis_name for p in problems]) if problems else "None recorded."

        # 3. Automatically gather Clinical Notes
        notes = ClinicalNote.query.filter_by(patient_id=patient.id).all()
        notes_text = "; ".join([f"{n.note_type}: {n.assessment}" for n in notes]) if notes else "None recorded."

        # 4. Safely gather Current Prescriptions from dispensing or pharmacy models
        meds_text = "None recorded."
        try:
            from models.dispensing import Prescription
            prescriptions = Prescription.query.filter_by(patient_id=patient.id).all()
            meds_text = ", ".join([p.medication.medication_name for p in prescriptions if p.medication]) if prescriptions else "None recorded."
        except Exception:
            try:
                from models.pharmacy import Prescription
                prescriptions = Prescription.query.filter_by(patient_id=patient.id).all()
                meds_text = ", ".join([p.medication.medication_name for p in prescriptions if p.medication]) if prescriptions else "None recorded."
            except Exception:
                pass

        # Construct comprehensive clinical prompt for Gemini
        prompt = f"""You are an advanced Clinical Decision Support AI integrated into an EMR system. Perform a comprehensive clinical review for patient {patient.full_name}:

【PATIENT DATA】
- Active Problems / Diagnoses: {problems_text}
- Recent Clinical Notes: {notes_text}
- Current Medications: {meds_text}
- Laboratory Results:
{raw_labs_text}

【YOUR TASKS】
1. **Clinical Analysis**: Identify critical or abnormal lab values (e.g., critically high glucose, deranged kidney function).
2. **Prescription Recommendations (What to Prescribe)**: Suggest evidence-based pharmacological interventions based on the labs and problems.
3. **Safety & Withhold Warnings (What NOT to Prescribe)**: Explicitly state which drugs should be withheld or avoided based on these specific lab values and diagnoses.
4. **Interference & Interaction Audit**: Check for potential adverse interactions or interferences between your suggested interventions and the patient's *Current Medications*.

Keep your response structured, highly professional, concise, and formatted with clear headings and bullet points."""

        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt
            )
            ai_analysis = response.text
        except Exception as e:
            ai_analysis = f"AI Error: Unable to complete analysis. Details: {str(e)}"
            
        summary_record = f"Labs:\n{raw_labs_text}\n\nProblems: {problems_text}\n\nMedications: {meds_text}"
        
        new_record = AILabRecord(
            patient_id=patient.id, 
            raw_text=summary_record, 
            ai_analysis=ai_analysis
        )
        db.session.add(new_record)
        db.session.commit()
        
        flash("Automated AI Clinical Review completed successfully.", "success")
        return redirect(url_for('patient_profile', patient_id=patient.id))