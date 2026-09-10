from app import create_app
from extensions import db
from models.medication import Medication

app = create_app()

EGYPTIAN_DRUG_INDEX = [
    # Analgesics & NSAIDs
    {"code": "EGY-MED-001", "trade": "Cataflam", "generic": "Diclofenac Potassium", "strength": "50 mg", "form": "Tablet", "category": "NSAID"},
    {"code": "EGY-MED-002", "trade": "Voltaren", "generic": "Diclofenac Sodium", "strength": "75 mg/3ml", "form": "Ampoule", "category": "NSAID"},
    {"code": "EGY-MED-003", "trade": "Brufen", "generic": "Ibuprofen", "strength": "400 mg", "form": "Tablet", "category": "NSAID"},
    {"code": "EGY-MED-004", "trade": "Brufen", "generic": "Ibuprofen", "strength": "600 mg", "form": "Tablet", "category": "NSAID"},
    {"code": "EGY-MED-005", "trade": "Panadol Extra", "generic": "Paracetamol / Caffeine", "strength": "500 mg / 65 mg", "form": "Tablet", "category": "Analgesic"},
    {"code": "EGY-MED-006", "trade": "Panadol Advance", "generic": "Paracetamol", "strength": "500 mg", "form": "Tablet", "category": "Analgesic"},
    {"code": "EGY-MED-007", "trade": "Paramol", "generic": "Paracetamol", "strength": "500 mg", "form": "Tablet", "category": "Analgesic"},
    {"code": "EGY-MED-008", "trade": "Ketofan", "generic": "Ketoprofen", "strength": "50 mg", "form": "Capsule", "category": "NSAID"},
    {"code": "EGY-MED-009", "trade": "Antinal", "generic": "Nifuroxazide", "strength": "200 mg", "form": "Capsule", "category": "Antidiarrheal"},
    
    # Antibiotics & Anti-infectives
    {"code": "EGY-MED-010", "trade": "Augmentin", "generic": "Amoxicillin / Clavulanic Acid", "strength": "1 g", "form": "Tablet", "category": "Antibiotic"},
    {"code": "EGY-MED-011", "trade": "Augmentin", "generic": "Amoxicillin / Clavulanic Acid", "strength": "625 mg", "form": "Tablet", "category": "Antibiotic"},
    {"code": "EGY-MED-012", "trade": "Hibiotic", "generic": "Amoxicillin / Clavulanic Acid", "strength": "1 g", "form": "Tablet", "category": "Antibiotic"},
    {"code": "EGY-MED-013", "trade": "Curam", "generic": "Amoxicillin / Clavulanic Acid", "strength": "1 g", "form": "Tablet", "category": "Antibiotic"},
    {"code": "EGY-MED-014", "trade": "Amoxil", "generic": "Amoxicillin", "strength": "500 mg", "form": "Capsule", "category": "Antibiotic"},
    {"code": "EGY-MED-015", "trade": "Zithrokan", "generic": "Azithromycin", "strength": "500 mg", "form": "Capsule", "category": "Antibiotic"},
    {"code": "EGY-MED-016", "trade": "Ciprobay", "generic": "Ciprofloxacin", "strength": "500 mg", "form": "Tablet", "category": "Antibiotic"},
    {"code": "EGY-MED-017", "trade": "Tavanic", "generic": "Levofloxacin", "strength": "500 mg", "form": "Tablet", "category": "Antibiotic"},
    {"code": "EGY-MED-018", "trade": "Claforan", "generic": "Cefotaxime", "strength": "1 g", "form": "Vial", "category": "Antibiotic"},
    {"code": "EGY-MED-019", "trade": "Ceftriaxone", "generic": "Ceftriaxone", "strength": "1 g", "form": "Vial", "category": "Antibiotic"},
    {"code": "EGY-MED-020", "trade": "Flagyl", "generic": "Metronidazole", "strength": "500 mg", "form": "Tablet", "category": "Antiprotozoal / Antibiotic"},
    {"code": "EGY-MED-021", "trade": "Bactrim", "generic": "Sulfamethoxazole / Trimethoprim", "strength": "400/80 mg", "form": "Tablet", "category": "Antibiotic"},
    {"code": "EGY-MED-022", "trade": "Sutrim", "generic": "Sulfamethoxazole / Trimethoprim", "strength": "800/160 mg", "form": "Tablet", "category": "Antibiotic"},

    # Cardiovascular & Antihypertensive
    {"code": "EGY-MED-023", "trade": "Concor", "generic": "Bisoprolol", "strength": "5 mg", "form": "Tablet", "category": "Beta-Blocker"},
    {"code": "EGY-MED-024", "trade": "Concor", "generic": "Bisoprolol", "strength": "2.5 mg", "form": "Tablet", "category": "Beta-Blocker"},
    {"code": "EGY-MED-025", "trade": "Capoten", "generic": "Captopril", "strength": "25 mg", "form": "Tablet", "category": "ACE Inhibitor"},
    {"code": "EGY-MED-026", "trade": "Norvasc", "generic": "Amlodipine", "strength": "5 mg", "form": "Tablet", "category": "Calcium Channel Blocker"},
    {"code": "EGY-MED-027", "trade": "Exforge", "generic": "Amlodipine / Valsartan", "strength": "5/160 mg", "form": "Tablet", "category": "Antihypertensive"},
    {"code": "EGY-MED-028", "trade": "Natrilix SR", "generic": "Indapamide", "strength": "1.5 mg", "form": "Tablet", "category": "Diuretic"},
    {"code": "EGY-MED-029", "trade": "Aldactone", "generic": "Spironolactone", "strength": "25 mg", "form": "Tablet", "category": "Diuretic"},
    {"code": "EGY-MED-030", "trade": "Lasix", "generic": "Furosemide", "strength": "40 mg", "form": "Tablet", "category": "Diuretic"},
    {"code": "EGY-MED-031", "trade": "Ator", "generic": "Atorvastatin", "strength": "20 mg", "form": "Tablet", "category": "Statin"},
    {"code": "EGY-MED-032", "trade": "Lipitor", "generic": "Atorvastatin", "strength": "40 mg", "form": "Tablet", "category": "Statin"},
    {"code": "EGY-MED-033", "trade": "Crestor", "generic": "Rosuvastatin", "strength": "10 mg", "form": "Tablet", "category": "Statin"},
    {"code": "EGY-MED-034", "trade": "Plavix", "generic": "Clopidogrel", "strength": "75 mg", "form": "Tablet", "category": "Antiplatelet"},
    {"code": "EGY-MED-035", "trade": "Aspocid", "generic": "Acetylsalicylic Acid", "strength": "75 mg", "form": "Chewable Tablet", "category": "Antiplatelet"},

    # Diabetes & Endocrine
    {"code": "EGY-MED-036", "trade": "Cidophage", "generic": "Metformin", "strength": "500 mg", "form": "Tablet", "category": "Antidiabetic"},
    {"code": "EGY-MED-037", "trade": "Cidophage Retard", "generic": "Metformin", "strength": "850 mg", "form": "Tablet", "category": "Antidiabetic"},
    {"code": "EGY-MED-038", "trade": "Glucophage", "generic": "Metformin", "strength": "1000 mg", "form": "Tablet", "category": "Antidiabetic"},
    {"code": "EGY-MED-039", "trade": "Amaryl", "generic": "Glimepiride", "strength": "2 mg", "form": "Tablet", "category": "Antidiabetic"},
    {"code": "EGY-MED-040", "trade": "Amaryl", "generic": "Glimepiride", "strength": "3 mg", "form": "Tablet", "category": "Antidiabetic"},
    {"code": "EGY-MED-041", "trade": "Galvus Met", "generic": "Vildagliptin / Metformin", "strength": "50/1000 mg", "form": "Tablet", "category": "Antidiabetic"},
    {"code": "EGY-MED-042", "trade": "Jardiance", "generic": "Empagliflozin", "strength": "10 mg", "form": "Tablet", "category": "Antidiabetic"},
    {"code": "EGY-MED-043", "trade": "Eltroxin", "generic": "Levothyroxine", "strength": "50 mcg", "form": "Tablet", "category": "Thyroid"},

    # Gastrointestinal & Antacids
    {"code": "EGY-MED-044", "trade": "Controloc", "generic": "Pantoprazole", "strength": "40 mg", "form": "Tablet", "category": "PPI"},
    {"code": "EGY-MED-045", "trade": "Nexium", "generic": "Esomeprazole", "strength": "40 mg", "form": "Tablet", "category": "PPI"},
    {"code": "EGY-MED-046", "trade": "Gastrazole", "generic": "Omeprazole", "strength": "20 mg", "form": "Capsule", "category": "PPI"},
    {"code": "EGY-MED-047", "trade": "Motilium", "generic": "Domperidone", "strength": "10 mg", "form": "Tablet", "category": "Antiemetic"},
    {"code": "EGY-MED-048", "trade": "Spasmo-Digestin", "generic": "Digestive Enzymes / Antispasmodic", "strength": "Standard", "form": "Tablet", "category": "Antispasmodic"},
    {"code": "EGY-MED-049", "trade": "Duspatalin Retard", "generic": "Mebeverine", "strength": "200 mg", "form": "Capsule", "category": "Antispasmodic"},

    # Respiratory & Allergy
    {"code": "EGY-MED-050", "trade": "Zyrtec", "generic": "Cetirizine", "strength": "10 mg", "form": "Tablet", "category": "Antihistamine"},
    {"code": "EGY-MED-051", "trade": "Claritine", "generic": "Loratadine", "strength": "10 mg", "form": "Tablet", "category": "Antihistamine"},
    {"code": "EGY-MED-052", "trade": "Telfast", "generic": "Fexofenadine", "strength": "180 mg", "form": "Tablet", "category": "Antihistamine"},
    {"code": "EGY-MED-053", "trade": "Ventolin", "generic": "Salbutamol", "strength": "100 mcg", "form": "Inhaler", "category": "Bronchodilator"}
]

with app.app_context():
    count_added = 0
    for item in EGYPTIAN_DRUG_INDEX:
        display_name = f"{item['trade']} ({item['generic']})"
        
        # Check by code or name
        existing = Medication.query.filter(
            (Medication.medication_code == item['code']) |
            (Medication.medication_name == display_name)
        ).first()

        if not existing:
            med = Medication(
                medication_code=item['code'],
                medication_name=display_name,
                dosage_form=item['form'],
                strength=item['strength'],
                category=item['category'],
                is_active=True,
                is_deleted=False
            )
            db.session.add(med)
            db.session.commit()
            count_added += 1

    print(f"DONE! Successfully added {count_added} Egyptian medications to the database.")