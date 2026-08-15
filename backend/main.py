from typing import Any
from operator import index
from pandas.core.methods.to_dict import to_dict
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from queries.analysis import job_postings
from datetime import datetime
import google.generativeai as genai
import os
import json
from pydantic import BaseModel
from queries.analysis import topSkills,topLocations,current_year_postings,toproles,common_skills,get_percentage_ofskills
from typing import List,Dict,Any


load_dotenv()


# -------------BASE MODELS------------------------
class ComparitiveModel(BaseModel):
    pass

class RolesPostingsModel(ComparitiveModel):
    roles :List[str]

class CommonSkillModal(ComparitiveModel):
    roles : List[str]

class ComparitiveInsightsModal(ComparitiveModel):
    role_frequency : List[Any]
    common_skill : List[Any]


app = FastAPI()

# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key= os.getenv("GEMINI_API"))
def get_ai_data(job_posting_data):
    prompt = f"""
        You are a job market analyst. You are given monthly job posting data for a specific year.
        Data (JSON format - month name and number of job postings):
        {job_posting_data}

        Analyze this data and return a SINGLE JSON object with exactly 2 keys:
        - "brief": 5-7 words. The single most important takeaway (e.g. peak month or trend).
        - "detail": 2 sentences, max 40 words. Cover: peak month with count, lowest month with count, and one trend observation.

        Return ONLY a raw JSON object (no markdown, no extra text):
        {{"brief": "...", "detail": "..."}}
        """
    try:
        model = genai.GenerativeModel('gemini-flash-lite-latest')
        model_response = model.generate_content(prompt)
        raw = model_response.text.strip()

        if not raw:
            print("Gemini returned empty response")
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
        print(f"Failed to generate response: {e}")
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
            print("Gemini returned empty response")
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
        print(f"Failed to generate comparative insights: {e}")
        return {}



@app.get('/api/job-postings')
def get_job_postings(year: int = datetime.now().year):
    data = job_postings(year)
    return data.to_dict(orient='records')



@app.get('/api/job-posting-card-insights')
def get_job_posting_insights(year: int = datetime.now().year):
    data = get_job_postings(year)
    res = get_ai_data(data)
    return res


@app.get('/api/job-tiles')
def get_data_for_jobtile():
    skill = topSkills().iloc[0]['name']
    location = topLocations().iloc[0]['location']
    year_posting = int(current_year_postings(datetime.now().year))
    return {
        "skill": skill,
        "location": location,
        "year_posting": f"{year_posting:,}"
    }


@app.get('/api/top-role-table')
def get_top_roles():
    data = toproles()
    return data.to_dict(orient='records')


@app.post('/api/get-role-posting')
def get_role_postings(request:RolesPostingsModel):
    role_list = [role.lower() for role in request.roles]
    data = toproles()
    filtered_data = data[data['role'].str.lower().isin(role_list)]
    return filtered_data.to_dict(orient='records')
    

@app.post('/api/common-skill')
def get_common_skill(request:CommonSkillModal):
    df = get_percentage_ofskills(request.roles)
    pivot_df = df.pivot(index='skill', columns = 'title', values='percentage').reset_index().fillna(0)
    return pivot_df.to_dict(orient='records')


@app.post('/api/get-comparitive-insights')
def get_comparitive_insights(request:ComparitiveInsightsModal):
    roles_frequency = request.role_frequency
    common_skills = request.common_skill
    insights = comparitive_insights(roles_frequency,common_skills)
    return insights


    


if __name__ == '__main__':
    print(get_common_skill(['full stack developer','data scientist','data engineer']))









    
    


