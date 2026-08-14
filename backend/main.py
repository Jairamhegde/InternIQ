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
from queries.analysis import topSkills,topLocations,current_year_postings,toproles,common_skills
from typing import List


load_dotenv()


# -------------BASE MODELS------------------------
class ComparitiveModel(BaseModel):
    pass

class RolesPostingsModel(ComparitiveModel):
    roles :List[str]

class CommonSkillModal(ComparitiveModel):
    roles : List[str]


app = FastAPI()

# Allow React app (localhost:5173) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
def get_common_skill(request):
    roles = request
    df = common_skills(roles)
    return df.to_dict(orient='records')



if __name__ == '__main__':
    print(get_common_skill(['full stack developer','data scientist','data engineer']))









    
    


