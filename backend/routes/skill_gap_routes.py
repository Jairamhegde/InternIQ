from fastapi import APIRouter, Form, UploadFile, File

from queries.skill_gap import find_freq_skills
from backend.crud import extract_pdf, extract_docx, analyze_gap

router = APIRouter(tags=["skill_gap"])


@router.post("/analyze-gap")
def skill_gap_analyzer(field: str = Form(...), resume: UploadFile = File(...)):
    file_byte = resume.file

    if resume.filename.lower().endswith(".pdf"):
        text = extract_pdf(file_byte)
    elif resume.filename.lower().endswith(".docx"):
        text = extract_docx(file_byte)
    else:
        return {"error": "Unsupported file type."}

    df = find_freq_skills(field)
    df_fre = dict(zip(df["skill"], df["term_freq"]))

    matched, missing = analyze_gap(text, set(df_fre.keys()))

    average_score = sum(df_fre[j] for j in missing) / len(missing) if missing else 0

    # Label each missing skill 'e' (essential) if its frequency is above average, else 'r' (required).
    missing_with_freq = [{"skill": s, "freq": df_fre[s], "priority": "e" if df_fre[s] >= average_score else "r"} for s in missing]
    matched_with_freq = [{"skill": s, "freq": df_fre[s]} for s in matched]

    matched_with_freq.sort(key=lambda x: x['freq'], reverse=True)
    missing_with_freq.sort(key=lambda x: x['freq'], reverse=True)

    return {
        "matched": matched_with_freq,
        "missing": missing_with_freq
    }
