import json
import os
import requests
from google import genai
from google.genai import types

OPENFDA_LABEL_URL = "https://api.fda.gov/drug/label.json"


def check_openfda_warnings(medication_name):
    """Fetches official boxed warnings from the openFDA drug label API."""
    cleaned = medication_name.split("(")[0].strip()
    try:
        url = f'{OPENFDA_LABEL_URL}?search=openfda.brand_name:"{cleaned}"&limit=1'
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json().get("results", [{}])[0]
            boxed = data.get("boxed_warning", [])
            contraindications = data.get("contraindications", [])
            warnings = data.get("warnings", [])

            summary = []
            if boxed:
                summary.append(boxed[0][:300] + "...")
            elif contraindications:
                summary.append(contraindications[0][:300] + "...")
            elif warnings:
                summary.append(warnings[0][:300] + "...")

            return " | ".join(summary) if summary else None
    except Exception:
        pass
    return None


def _evaluate_rule_based_fallback(patient, target_medication_name, fda_notice=None):
    """Deterministic fallback engine when external AI API is unreachable."""
    alerts = []
    med_lower = target_medication_name.lower()

    # Aggregate conditions from problems
    active_problems = []
    for p in getattr(patient, "problems", []):
        if getattr(p, "is_deleted", False):
            continue
        if getattr(p, "clinical_status", "Active") != "Active":
            continue

        name = (
            getattr(p, "problem_name", None)
            or getattr(p, "diagnosis_name", None)
            or getattr(p, "diagnosis", None)
            or ""
        )
        code = getattr(p, "icd10_code", "") or ""
        if name or code:
            active_problems.append({"name": name.strip(), "code": code.strip()})

    # Aggregate conditions mentioned in unstructured clinical notes
    notes_text = ""
    for n in getattr(patient, "clinical_notes", []):
        if getattr(n, "is_deleted", False):
            continue
        notes_text += f" {getattr(n, 'chief_complaint', '')} {getattr(n, 'assessment', '')} {getattr(n, 'diagnosis_text', '')}"
    notes_text_lower = notes_text.lower()

    # 1. Check NSAID contraindications (CKD, hemodialysis, NSAID allergy)
    nsaids = ["aspirin", "aspocid", "ibuprofen", "brufen", "diclofenac", "cataflam", "voltaren", "ketofan", "ketoprofen"]
    if any(term in med_lower for term in nsaids):
        has_nsaid_allergy = any("aspirin" in item["name"].lower() or "nsaid" in item["name"].lower() or "z88.5" in item["code"].lower() for item in active_problems) or "nsaid" in notes_text_lower or "aspirin allergy" in notes_text_lower
        has_renal_issue = any("kidney" in item["name"].lower() or "renal" in item["name"].lower() or "ckd" in item["name"].lower() or "n18" in item["code"].lower() for item in active_problems) or "hemodialysis" in notes_text_lower or "dialysis" in notes_text_lower or "esrd" in notes_text_lower

        if has_nsaid_allergy:
            alerts.append({
                "severity": "LETHAL",
                "title": "Severe NSAID Anaphylactoid Risk",
                "detail": (
                    f"Documented severe allergy to NSAIDs. '{target_medication_name}' can trigger "
                    "acute bronchospasm, angioedema, and cardiovascular collapse."
                ),
                "fda_notice": fda_notice
            })
        if has_renal_issue:
            alerts.append({
                "severity": "LETHAL",
                "title": "Absolute Contraindication: Nephrotoxic Agent / Dialysis Risk",
                "detail": (
                    f"Patient has severe renal impairment/hemodialysis history. Systemic NSAIDs ('{target_medication_name}') "
                    "inhibit renal prostaglandins, precipitating loss of residual renal function, severe fluid retention, and hyperkalemic crisis."
                ),
                "fda_notice": fda_notice
            })

    # 2. Check Penicillin / Beta-lactams
    penicillin_family = ["amoxicillin", "amox", "ampicillin", "augmentin", "hibiotic", "curam", "penicillin", "clavulanic"]
    if any(term in med_lower for term in penicillin_family):
        has_penicillin_allergy = any("penicillin" in item["name"].lower() or "beta-lactam" in item["name"].lower() or "z88.0" in item["code"].lower() for item in active_problems) or "penicillin" in notes_text_lower
        if has_penicillin_allergy:
            alerts.append({
                "severity": "LETHAL",
                "title": "Lethal Anaphylaxis Risk: Penicillin / Beta-Lactam Hypersensitivity",
                "detail": (
                    f"Patient has documented hypersensitivity to Beta-Lactams. "
                    f"Administering '{target_medication_name}' carries an immediate risk of fatal "
                    "anaphylactic shock and airway collapse."
                ),
                "fda_notice": fda_notice or "FDA Warning: Serious hypersensitivity reactions reported."
            })

    return alerts


def evaluate_prescription_safety(patient, target_medication_name):
    """
    AI-driven Clinical Decision Support (CDS) engine using Google GenAI API.
    Evaluates both structured problems and free-text clinical notes.
    """
    fda_notice = check_openfda_warnings(target_medication_name)
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return _evaluate_rule_based_fallback(patient, target_medication_name, fda_notice)

    # 1. Format Structured Problems
    problems_list = []
    for p in getattr(patient, "problems", []):
        if getattr(p, "is_deleted", False) or getattr(p, "clinical_status", "Active") != "Active":
            continue
        name = getattr(p, "diagnosis_name", None) or getattr(p, "problem_name", "Unknown Problem")
        code = getattr(p, "icd10_code", "N/A")
        problems_list.append(f"- {name} (ICD-10: {code})")

    problems_text = "\n".join(problems_list) if problems_list else "No active formal diagnoses recorded."

    # 2. Format Unstructured Clinical Notes (Captures dialysis, symptoms, free-text warnings)
    notes_list = []
    for n in getattr(patient, "clinical_notes", []):
        if getattr(n, "is_deleted", False):
            continue
        note_type = getattr(n, "note_type", "Clinical Note")
        cc = getattr(n, "chief_complaint", "")
        assessment = getattr(n, "assessment", "")
        diag = getattr(n, "diagnosis_text", "")
        plan = getattr(n, "plan", "")
        notes_list.append(
            f"[{note_type}] Chief Complaint: {cc} | Assessment: {assessment} | Diagnosis: {diag} | Plan: {plan}"
        )

    # Use the 5 most recent notes for prompt context
    notes_text = "\n".join(notes_list[-5:]) if notes_list else "No previous clinical notes recorded."

    # 3. Build Clinical Prompt
    prompt = f"""
You are an expert Clinical Decision Support (CDS) AI engine integrated into a hospital EHR.
Evaluate whether prescribing the target medication presents severe contraindications, major drug-disease interactions, or life-threatening allergy risks for this patient.
Crucial: Carefully review BOTH the formal diagnoses AND the free-text clinical notes (e.g., hemodialysis, undocumented allergies, renal failure, liver disease).

[PATIENT CLINICAL PROFILE]
Full Name: {patient.full_name}

Active Problems & Diagnoses:
{problems_text}

Recent Clinical Notes & Physician Assessments:
{notes_text}

[TARGET MEDICATION TO PRESCRIBE]
{target_medication_name}

[OPENFDA REGULATORY INFORMATION]
{fda_notice or "No boxed warning found on openFDA"}

[TASK]
Analyze the clinical compatibility.
- If the drug is clinically safe or only has routine mild side effects, return an empty JSON array: []
- If an absolute contraindication, fatal allergy, or major organ toxicity risk exists (such as NSAIDs in hemodialysis / ESRD, NSAIDs in documented allergy, or Penicillins in Beta-lactam allergy), return a JSON array containing alert objects.

Schema:
[
  {{
    "severity": "LETHAL" | "CRITICAL" | "WARNING",
    "title": "Short descriptive clinical title",
    "detail": "Pathophysiological and pharmacological explanation of the contraindication for this specific patient.",
    "fda_notice": "Relevant regulatory warning or boxed warning excerpt"
  }}
]
"""

    # 4. Request Inference
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            ),
        )

        if response.text:
            parsed_alerts = json.loads(response.text)
            if isinstance(parsed_alerts, list):
                for alert in parsed_alerts:
                    if not alert.get("fda_notice") and fda_notice:
                        alert["fda_notice"] = fda_notice
                return parsed_alerts
    except Exception as e:
        print(f"[CDS AI Error] Falling back to rule engine: {e}")

    return _evaluate_rule_based_fallback(patient, target_medication_name, fda_notice)