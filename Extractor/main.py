from fastapi import FastAPI
from bson import ObjectId
import tempfile
import os
import pandas as pd
from datetime import datetime
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_path = os.path.join(project_root, 'DB')

sys.path.append(project_root)
sys.path.append(db_path)

from extractor import SkillExtractor, read_file
from DB.DB_Management import DBManagement

app = FastAPI()

# -----------------------------
# CONFIG
# -----------------------------
SKILLS_CSV = "Skills.csv"
SKILL_COLUMN = "Example"
SIMILARITY = 0.80


def load_skills(csv_path: str, column: str):
    df = pd.read_csv(csv_path)

    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found.")

    skills = (
        df[column]
        .dropna()
        .str.lower()
        .str.strip()
    )

    skills = skills[skills.str.len() > 2]
    skills = skills.drop_duplicates()

    return skills.tolist()


# Load once
skills_list = load_skills(SKILLS_CSV, SKILL_COLUMN)
extractor = SkillExtractor(skills_list)

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "DB", ".env"))

db_manager = DBManagement()


@app.post("/extract")
def extract(data: dict):
    resume_id = data.get("resumeId")

    if not resume_id:
        return {"error": "resumeId required"}

    print(f"[Extractor] Received resumeId: {resume_id}")

    try:
        resume_id_obj = ObjectId(resume_id)
    except:
        return {"error": "Invalid resumeId"}

    # -----------------------------
    # FETCH RESUME
    # -----------------------------
    resumes = db_manager.fetch(
        collection_name="Resumes",
        filter={"_id": resume_id_obj}
    )

    print(f"[Extractor] Fetch result count: {len(resumes)}")

    if not resumes or len(resumes) == 0:
        return {"error": "Resume not found"}

    resume = resumes[0]
    binary_data = resume.get("data")

    if not binary_data:
        return {"error": "No file data found"}

    # -----------------------------
    # SAVE TEMP FILE
    # -----------------------------
    suffix = ".pdf"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(binary_data)
        temp_path = tmp.name

    print(f"[Extractor] Temp file created: {temp_path}")

    try:
        # -----------------------------
        # READ TEXT
        # -----------------------------
        text = read_file(temp_path)

        if not text or len(text.strip()) == 0:
            print("[Extractor] No text extracted")
            return {"error": "Failed to extract text"}

        print(f"[Extractor] Text length: {len(text)}")

        # -----------------------------
        # EXTRACT SKILLS
        # -----------------------------
        resume_skills = extractor.extract(text, SIMILARITY)

        print(f"[Extractor] Skills extracted: {len(resume_skills)}")

        # -----------------------------
        # STORE IN DB
        # -----------------------------
        db_manager.update_value(
            flt={"_id": resume_id_obj},
            attribute="extractedKeywords",
            new_value=resume_skills,
            collection_name="Resumes"
        )

        print("[Extractor] DB updated successfully")

        return {
            "resumeId": resume_id,
            "skills": resume_skills
        }

    except Exception as e:
        print(f"[Extractor ERROR] {e}")
        return {"error": str(e)}

    finally:
        os.remove(temp_path)
        print("[Extractor] Temp file deleted")