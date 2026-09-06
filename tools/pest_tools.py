from agents import function_tool
from database.db_setup import get_connection
from models.schemas import PestDiagnosis


@function_tool
def pest_doctor(crop_name: str, symptoms: str) -> PestDiagnosis:
    """Diagnose a pest or disease based on described symptoms and suggest safe treatment.

    Args:
        crop_name: Name of the affected crop
        symptoms: Farmer's description of symptoms (e.g. 'leaves curling, white insects')
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pest_disease WHERE crop_name = ?", (crop_name,))
    rows = cursor.fetchall()
    conn.close()

    symptoms_lower = symptoms.lower()
    for row in rows:
        keywords = row["symptom_keywords"].lower().split(", ")
        if any(keyword in symptoms_lower for keyword in keywords):
            return PestDiagnosis(
                pest_name=row["pest_name"],
                treatment=row["treatment"],
                safe_dosage=row["safe_dosage"],
                confidence_note="Matched based on described symptoms."
            )

    return PestDiagnosis(
        pest_name="Unknown",
        treatment="Consult a local agriculture extension officer for accurate diagnosis.",
        safe_dosage="N/A",
        confidence_note="No matching symptoms found in database."
    )