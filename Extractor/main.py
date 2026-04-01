"""
main.py
-------
Extract all skills from ONE resume and print them.
Also saves them to a file.
"""

import pandas as pd
from pathlib import Path

from extractor import SkillExtractor, read_file


# ── Config ─────────────────────────────────────────────────────

RESUME_FILE   = "resumes/my_resume.pdf"
JOB_DESC_FILE = "job_description.txt"
SKILLS_CSV    = "Skills.csv"
SKILL_COLUMN  = "Example"

SIMILARITY = 0.80   # balanced threshold


# ── Load skills ────────────────────────────────────────────────

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

    # Clean dataset
    skills = skills[skills.str.len() > 2]
    skills = skills.drop_duplicates()

    print(f"Loaded {len(skills)} total skills")

    return skills.tolist()


# ── Match logic ────────────────────────────────────────────────

def compute_match(resume_skills, job_skills):

    resume_set = set(resume_skills)
    job_set    = set(job_skills)

    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)

    score = round(len(matched) / len(job_set) * 100, 1) if job_set else 0

    return matched, missing, score


# ── Main ──────────────────────────────────────────────────────

def main():

    print("Loading skill dataset...")
    skills = load_skills(SKILLS_CSV, SKILL_COLUMN)

    print("Initializing extractor...")
    extractor = SkillExtractor(skills)

    # ── JOB DESCRIPTION ──
    print("\nReading job description...")
    job_text = Path(JOB_DESC_FILE).read_text(encoding="utf-8")

    job_skills = extractor.extract(job_text, SIMILARITY)
    print(f"Job skills found: {len(job_skills)}")

    # ── RESUME ──
    resume_path = Path(RESUME_FILE)

    if not resume_path.exists():
        print(f"Resume not found: {RESUME_FILE}")
        return

    print(f"\nAnalyzing: {resume_path.name}")

    resume_text = read_file(resume_path)
    resume_skills = extractor.extract(resume_text, SIMILARITY)

    # ── PRINT RESUME SKILLS ──
    print("\n===== RESUME SKILLS =====\n")
    for skill in resume_skills:
        print(f"- {skill}")

    print(f"\nTotal resume skills: {len(resume_skills)}")

    # ── MATCHING ──
    matched, missing, score = compute_match(resume_skills, job_skills)

    print("\n===== MATCH RESULT =====\n")
    print(f"Match Score: {score}%")

    print("\nMatched Skills:")
    for s in matched:
        print(f"- {s}")

    print("\nMissing Skills:")
    for s in missing:
        print(f"- {s}")

    # ── SAVE OUTPUT ──
    with open("extracted_skills.txt", "w", encoding="utf-8") as f:
        f.write("RESUME SKILLS:\n")
        for s in resume_skills:
            f.write(s + "\n")

        f.write("\nJOB SKILLS:\n")
        for s in job_skills:
            f.write(s + "\n")

        f.write("\nMATCHED SKILLS:\n")
        for s in matched:
            f.write(s + "\n")

        f.write("\nMISSING SKILLS:\n")
        for s in missing:
            f.write(s + "\n")

    print("\nSaved results to extracted_skills.txt")


if __name__ == "__main__":
    main()