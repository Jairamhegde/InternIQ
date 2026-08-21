import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import pandas as pd
import google.generativeai as genai
import fitz
from docx import Document

from queries.analysis import (
    job_postings, topSkills, topLocations, current_year_postings, toproles,
    common_skills, get_percentage_ofskills, build_tfidf_scores, find_reuiqred_skills, find_freq_skills
)
from queries.recent_market_trends import (
    Top_role, top_skill, total_opportunities, average_salary, 
    recenttopLocations, previous_total_opportunities, recent_job_postings
)


load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://intern-iq-five.vercel.app"
    ],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
   
)

genai.configure(api_key=os.getenv("GEMINI_API"))


# -------------BASE MODELS------------------------

class Basemodel(BaseModel):
    pass


class OverviewInsightsModel(Basemodel):
    year: int = Field(default_factory=lambda: datetime.now().year)
    tile_data: Dict[str, Any]
    field: str = 'all'


class RolesPostingsModel(Basemodel):
    roles: List[str]


class CommonSkillModal(Basemodel):
    roles: List[str]


class ComparitiveInsightsModal(Basemodel):
    role_frequency: List[Any]
    common_skill: List[Any]


class JobpostingModel(BaseModel):
    year: int
    field: str


# ------------- HELPER FUNCTIONS ------------------------

def market_overview_insights(job_posting_data, tile_data):
    prompt = f"""
        You are a job market analyst. You are given monthly job posting data for a specific year.
        Data (JSON format - month name and number of job postings):
        {job_posting_data}
        and most mentioned location and skill and total number of postings :{tile_data}

        Analyze this data and return a SINGLE JSON object with exactly 3 keys:
        - "brief": 5-7 words. The single most important takeaway (e.g. peak month or trend).
        - "detail": 2 sentences, max 40 words. Cover: peak month with count, lowest month with count, and one trend observation.
        - "overview" : 3-4 line sentence, cover most mentioned location, skill and total postings recorded till no. explai that in brief.
        Return ONLY a raw JSON object (no markdown, no extra text):
        {{"brief": "...", "detail": "...", "overview": "..."}}
        """
    try:
        model = genai.GenerativeModel('gemini-flash-lite-latest')
        model_response = model.generate_content(prompt)
        raw = model_response.text.strip()

        if not raw:
            return []

        # Strip markdown code blocks if model added them despite instructions
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        clean_response = json.loads(raw)
        return clean_response
    except Exception as e:
        return []


def comparitive_insights(role_freq, common_skills):
    prompt = f"""
        # Persona
        You are an elite Labor Market Data Scientist and Career Intelligence Strategist. You specialize in analyzing job market trends, skills gaps, and hiring demands. Your insights are data-driven, actionable, and tailored to help tech professionals and executives make strategic career decisions.

        # Objective
        Analyze the comparative hiring demand and skill requirements between the following job roles to generate a high-value, concise executive summary.

        # Input Data
        1. Role Hiring Volume (Total Job Postings):
        {json.dumps(role_freq, indent=2)}

        2. Skill Matrix & Percentage Distribution (How often skills appear for these roles):
        {json.dumps(common_skills, indent=2)}

        # Output Requirements
        Analyze the data and return a SINGLE JSON object with exactly 3 keys:
        - "role_insights": 1-2 concise sentences analyzing the hiring demand. Identify the dominant role in terms of total postings and highlight the volume gap or trend.
        - "skill_insights": 1-2 concise sentences analyzing the skill matrix. Identify the foundational skills shared across the roles, and pinpoint the specialized skills that differentiate them.
        - "takeaway": One strategic, forward-looking takeaway. Offer actionable advice for a candidate trying to pivot between these roles or maximize their marketability.

        # Tone and Style
        - Professional, analytical, and authoritative.
        - Avoid fluff; be direct and data-centric.
        - Do not use first-person pronouns ("I", "we").

        Return ONLY a valid, raw JSON object (no markdown, no backticks, no extra text):
        {{"role_insights": "...", "skill_insights": "...", "takeaway": "..."}}
    """
    try:
        model = genai.GenerativeModel('gemini-flash-lite-latest')
        model_response = model.generate_content(prompt)
        raw = model_response.text.strip()
        
        if not raw:  
            return {}

        # Strip markdown code blocks if model added them despite instructions
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        clean_response = json.loads(raw)
        return clean_response
    except Exception as e:
        return {}


# _________________________ API ENDPOINTS ______________________

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API is running"}


@app.post('/api/job-postings')
def get_job_postings(request: JobpostingModel):
    actual_field = None if request.field.lower() == 'all' else request.field
    data = job_postings(request.year, actual_field)
    return data.to_dict(orient='records')


@app.post('/api/job-posting-card-insights')
def get_job_posting_insights(request: OverviewInsightsModel):
    actual_field = None if request.field.lower() == 'all' else request.field
    data = job_postings(request.year, actual_field)
    res = market_overview_insights(data, request.tile_data)
    return res


@app.get('/api/job-tiles')
def get_data_for_jobtile(field: str = 'all'):
    actual_field = None if field.lower() == 'all' else field
    skill = topSkills(actual_field).iloc[0]['name']
    location = topLocations(actual_field).iloc[0]['location']
    toprole = toproles(actual_field).iloc[0]['role']
    year_posting = int(current_year_postings(datetime.now().year, actual_field))
    
    return {
        "skill": skill,
        "location": location,
        "year_posting": f"{year_posting:,}",
        "role": toprole
    }


@app.get('/api/top-role-table')
def get_top_roles(field: str = 'all'):
    actual_field = None if field.lower() == 'all' else field
    data = toproles(actual_field)
    return data.to_dict(orient='records')


@app.post('/api/get-role-posting')
def get_role_postings(request: RolesPostingsModel):
    role_list = [role.lower() for role in request.roles]
    data = toproles()
    filtered_data = data[data['role'].str.lower().isin(role_list)]
    return filtered_data.to_dict(orient='records')


@app.post('/api/common-skill')
def get_common_skill(request: CommonSkillModal):
    df = get_percentage_ofskills(request.roles)
    pivot_df = df.pivot(index='skill', columns='title', values='percentage').reset_index().fillna(0)
    return pivot_df.to_dict(orient='records')


@app.post('/api/get-comparitive-insights')
def get_comparitive_insights(request: ComparitiveInsightsModal):
    roles_frequency = request.role_frequency
    common_skills = request.common_skill
    insights = comparitive_insights(roles_frequency, common_skills)
    return insights


# _________________________ Recent Market Trends Endpoints ______________________

@app.get("/api/recent-market-trend")
def get_recent_trends():
    df_top_role = Top_role()
    df_top_skill = top_skill()
    df_opportunities = total_opportunities()
    df_toplocation = recenttopLocations()
    pre_total_opp = previous_total_opportunities()

    top_role = df_top_role.iloc[0]["title"] if not df_top_role.empty else None
    top_role_count = int(df_top_role.iloc[0]["job_count"]) if not df_top_role.empty else 0

    avg_sal = None
    if top_role:
        df_avg_sal = average_salary(top_role)
        if not df_avg_sal.empty and pd.notnull(df_avg_sal.iloc[0]['average']):
            avg_sal = float(df_avg_sal.iloc[0]['average'])

    top_skilll = df_top_skill.iloc[0]["skill"] 
    top_skilll_count = int(df_top_skill.iloc[0]["skill_count"])

    total_opportunity = int(df_opportunities.iloc[0]["total_opportunities"])

    top_location = df_toplocation.iloc[0]['location']
    top_location_count = int(df_toplocation.iloc[0]['count'])

    chart_data = df_top_role.rename(columns={"title": "role", "job_count": "volume"}).to_dict(orient='records')
    
    prev_opportunity = int(pre_total_opp.iloc[0]["total_opportunities"]) if not pre_total_opp.empty else 0

    if prev_opportunity > 0:
        increment = round(((total_opportunity - prev_opportunity) / prev_opportunity) * 100, 2)
    else:
        increment = 100.0 if total_opportunity > 0 else 0.0

    return {
        "role": [top_role, top_role_count],
        "skill": [top_skilll, top_skilll_count],
        "postings": total_opportunity,
        "increment": increment,
        "toproles": chart_data,
        "toplocation": [top_location, top_location_count],
        "average_sal": avg_sal if avg_sal else None
    }


@app.get('/api/job-posting-list')
def job_posting_list():
    df = recent_job_postings()
    # Convert dates to a clean string format (YYYY-MM-DD) so they don't look like random epoch numbers
    df['posted_date'] = pd.to_datetime(df['posted_date']).dt.strftime('%Y-%m-%d')
    # Use to_json to safely serialize Pandas data and NaNs!
    return json.loads(df.to_json(orient='records'))

@app.get("/api/get-top-locations")
def get_top_locations():
    location = recenttopLocations()
    top_4 = location.iloc[:4][:]

    top_4 = top_4.rename(columns={"location":"name","count":"value"})
    data = top_4.to_dict(orient='records')
   
    COLORS = ['#f43f5e', '#f97316', '#f59e0b', '#facc15']
    for i,j in enumerate(data):
        j['fill'] = COLORS[i % len(COLORS)]

    return data



# _________________________ Skill Gap Analyzer Endpoints ________________________

def extract_pdf(file):
    data = fitz.open(stream=file.read(), filetype='pdf')
    text = ""
    for page in data:
        text += page.get_text()
    return text


def extract_docx(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


tf_idf = build_tfidf_scores()


def analyze_gap(text, required_set):
    matched_skill = set()
    missing_skill = set()
    for skill in required_set:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            matched_skill.add(skill)
        else:
            missing_skill.add(skill)
    return matched_skill, missing_skill


@app.post("/api/analyze-gap")
def skillgap_analyzer(field: str = Form(...), resume: UploadFile = File(...)):
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
    
    # Calculate the average score (avoid division by zero if missing is empty)
    average_score = sum(df_fre[j] for j in missing) / len(missing) if missing else 0

    missing_with_freq = [{"skill": s, "freq": df_fre[s], "priority": "e" if df_fre[s] >= average_score else "r"} for s in missing]
    matched_with_freq = [{"skill": s, "freq": df_fre[s]} for s in matched]

    matched_with_freq.sort(key=lambda x: x['freq'], reverse=True)
    missing_with_freq.sort(key=lambda x: x['freq'], reverse=True)
    
    return {
        "matched": matched_with_freq,
        "missing": missing_with_freq
    }




if __name__ == '__main__':
    pass
