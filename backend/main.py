import logging
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
    common_skills, get_percentage_ofskills, find_reuiqred_skills, find_freq_skills
    ,top_hiring_company
)
from queries.recent_market_trends import (
    Top_role, top_skill, total_opportunities, average_salary, 
    recenttopLocations, previous_total_opportunities, recent_job_postings, get_last_sync_time
   
)

from queries.comparative_analysis import compare_role_trend

from backend.models import (
    OverviewInsightsModel, RolesPostingsModel, CommonSkillModal, 
    ComparativeInsightsModel, JobpostingModel, TopCompanyModel,LinechartData
)
from backend.crud import (
     extract_pdf, 
    extract_docx, analyze_gap,get_ai_response
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

# _________________________ API ENDPOINTS ______________________

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "API is running"}

@app.get("/api/last-sync")
def last_sync():
    return {"last_sync": get_last_sync_time()}

@app.post('/api/top-companies')
def get_top_companies(request:TopCompanyModel):
    actual_field = None if request.field.lower() == 'all' else request.field
    top_companies = top_hiring_company(request.year, actual_field)
    return top_companies.to_dict(orient='records')



@app.post('/api/job-postings')
def get_job_postings(request: JobpostingModel):
    actual_field = None if request.field.lower() == 'all' else request.field
    data = job_postings(request.year, actual_field)
    return data.to_dict(orient='records')


@app.post('/api/job-posting-card-insights')
async def get_job_posting_insights(request: OverviewInsightsModel):
    actual_field = None if request.field.lower() == 'all' else request.field
    data = job_postings(request.year, actual_field)
    data_dict = data.to_dict(orient='records')
    res = await get_ai_response(data_dict, request.tile_data, 'overview')
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


#---------------------Comparative analysis endpoints--------------------


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


@app.post('/api/get-comparative-insights')
async def get_comparative_insights(request: ComparativeInsightsModel):
    roles_frequency = request.role_frequency
    common_skills = request.common_skill
    insights = await get_ai_response(roles_frequency, common_skills, 'comparision')
    return insights

@app.post('/api/get-linechart-data')
def get_linechart_data(request:LinechartData):
    if not request.selected_jobs:
        return []
        
    df = compare_role_trend(*request.selected_jobs)
    
    if df is None or df.empty:
        return []
        
    return df.to_dict(orient='records')


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
        "average_sal": avg_sal 
    }


@app.get('/api/job-posting-list')
def job_posting_list():
    df = recent_job_postings()
    # Convert dates to a clean string format (YYYY-MM-DD) so they don't look like random epoch numbers
    df['posted_date'] = pd.to_datetime(df['posted_date']).dt.strftime('%Y-%m-%d')
    # Use to_json to safely serialize Pandas data and NaNs
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
    
    
    average_score = sum(df_fre[j] for j in missing) / len(missing) if missing else 0

    '''
    create dict which holds missing skills along with frequency, with label as 'e' (essential)
    or 'r' required. if freq > avg -> label as 'e'. else 'r'
    '''
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
