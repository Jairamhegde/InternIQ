from fastapi import Request
import asyncio
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
    top_hiring_company
)
from queries.recent_market_trends import (
    Top_role, top_skill, total_opportunities, average_salary,
    recenttopLocations, previous_total_opportunities, recent_job_postings, get_last_sync_time
)
from queries.comparative_analysis import (
    compare_role_trend, common_skills, get_percentage_ofskills, average_salary_by_role
)
from queries.skill_gap import find_reuiqred_skills, find_freq_skills
from queries.role_specific_analysis import role_details

from backend.models import (
    OverviewInsightsModel, RolesPostingsModel, CommonSkillModal, 
    ComparativeInsightsModel, JobpostingModel, TopCompanyModel,LinechartData, ChatModel
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
        "http://localhost:5174",
        "http://localhost:3000",
        "https://intern-iq-five.vercel.app"
    ],  
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

genai.configure(api_key=os.getenv("GEMINI_API"), transport="rest")


app.state.dashboard_data = {
    "pipeline": {},
    "market_overview": {},
    "comparative_analysis": {},
    "recent_market_trends": {},
}


def save_dashboard_data(page, data_name, filter_key, value):
    """Stores the latest result of an endpoint in app.state.dashboard_data."""
    page_data = app.state.dashboard_data[page]

    if data_name not in page_data:
        page_data[data_name] = {}

    page_data[data_name][filter_key] = value


# _________________________ API ENDPOINTS ______________________

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "API is running"}

@app.get("/api/last-sync")
def last_sync():
    result = {"last_sync": get_last_sync_time()}
    app.state.dashboard_data["pipeline"]["last_sync"] = result["last_sync"]
    return result

@app.post('/api/top-companies')
def get_top_companies(request:TopCompanyModel):
    actual_field = None if request.field.lower() == 'all' else request.field
    top_companies = top_hiring_company(request.year, actual_field,request.month)
    result = top_companies.to_dict(orient='records')

    filter_key = f"year={request.year}, field={request.field}, month={request.month}"
    save_dashboard_data("market_overview", "top_hiring_companies", filter_key, result)
    return result



@app.post('/api/job-postings')
def get_job_postings(request: JobpostingModel):
    actual_field = None if request.field.lower() == 'all' else request.field
    data = job_postings(request.year, actual_field)
    result = data.to_dict(orient='records')

    filter_key = f"year={request.year}, field={request.field}"
    save_dashboard_data("market_overview", "monthly_job_postings", filter_key, result)
    return result


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

    skills_df = topSkills(field=actual_field)
    skill = skills_df.iloc[0]['name'] if not skills_df.empty else "N/A"
    topSkillCount = int(skills_df.iloc[0]['demand']) if not skills_df.empty else 0

    loc_df = topLocations(field=actual_field)
    location = loc_df.iloc[0]['location'] if not loc_df.empty else "N/A"
    topLocCount = int(loc_df.iloc[0]['count']) if not loc_df.empty else 0
    
    roles_df = toproles(field=actual_field)
    toprole = roles_df.iloc[0]['role'] if not roles_df.empty else "N/A"
    toproleCount = int(roles_df.iloc[0]['volume']) if not roles_df.empty else 0
    
    year_posting = int(current_year_postings(datetime.now().year, field=actual_field))

    result = {
        "skill": skill,
        "skillCount":topSkillCount,

        "location": location,
        "locationCount":topLocCount,
        "year_posting": f"{year_posting:,}",
        "role": toprole,
        "roleCount":toproleCount

    }

    save_dashboard_data("market_overview", "summary_tiles", f"field={field}", result)
    return result


#---------------------Comparative analysis endpoints--------------------


@app.get('/api/top-role-table')
def get_top_roles(field: str = 'all', limit: int | None = None):
    actual_field = None if field.lower() == 'all' else field
    data = toproles(field=actual_field)
    if limit:
        data = data.head(limit)
    result = data.to_dict(orient='records')

    filter_key = f"field={field}" if not limit else f"field={field},limit={limit}"
    save_dashboard_data("market_overview", "top_roles", filter_key, result)
    return result


@app.get('/api/top-skills')
def get_top_skills(field: str = 'all', limit: int = 5):
    actual_field = None if field.lower() == 'all' else field
    data = topSkills(field=actual_field).head(limit)
    result = data.to_dict(orient='records')

    save_dashboard_data("market_overview", "top_skills", f"field={field}", result)
    return result


@app.post('/api/get-role-posting')
def get_role_postings(request: RolesPostingsModel):
    role_list = [role.lower() for role in request.roles]
    data = toproles()
    filtered_data = data[data['role'].str.lower().isin(role_list)]

    # Add each role's average salary; roles with no salary data get None.
    salary_df = average_salary_by_role(filtered_data['role'].tolist())
    if not salary_df.empty:
        salary_df = salary_df.rename(columns={'job_role': 'role'})
        filtered_data = filtered_data.merge(salary_df, on='role', how='left')
        filtered_data['average_salary'] = filtered_data['average_salary'].astype(object).where(
            filtered_data['average_salary'].notna(), None
        )

    result = filtered_data.to_dict(orient='records')

    filter_key = "roles=" + ", ".join(request.roles)
    save_dashboard_data("comparative_analysis", "total_postings_per_role", filter_key, result)
    return result


@app.post('/api/common-skill')
def get_common_skill(request: CommonSkillModal):
    df = get_percentage_ofskills(request.roles)
    pivot_df = df.pivot(index='skill', columns='title', values='percentage').reset_index().fillna(0)
    result = pivot_df.to_dict(orient='records')

    filter_key = "roles=" + ", ".join(request.roles)
    save_dashboard_data("comparative_analysis", "skill_share_percent_per_role", filter_key, result)
    return result


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

    result = df.to_dict(orient='records')

    filter_key = "roles=" + ", ".join(request.selected_jobs)
    save_dashboard_data("comparative_analysis", "monthly_postings_per_role", filter_key, result)
    return result


# _________________________ Role Specific Endpoints ______________________

@app.get('/api/role-details')
def get_role_details(role: str):
    details = role_details(role.lower())

    result = {
        "role": details["role"],
        "total_postings": details["total_postings"],
        "average_salary": details["average_salary"],
        "top_skills": details["top_skills"].to_dict(orient='records'),
        "monthly_postings": details["monthly_postings"].to_dict(orient='records'),
    }
    return result


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

    result = {
        "role": [top_role, top_role_count],
        "skill": [top_skilll, top_skilll_count],
        "postings": total_opportunity,
        "increment": increment,
        "toproles": chart_data,
        "toplocation": [top_location, top_location_count],
        "average_sal": avg_sal
    }

    # Saved with clearer names so the AI understands each value.
    summary_for_ai = {
        "total_postings_last_10_days": total_opportunity,
        "percent_change_vs_previous_10_days": increment,
        "top_role": {"role": top_role, "postings": top_role_count},
        "top_skill": {"skill": top_skilll, "mentions": top_skilll_count},
        "top_location": {"location": top_location, "postings": top_location_count},
        "average_stipend_of_top_role": avg_sal,
        "postings_per_role": chart_data,
    }
    save_dashboard_data("recent_market_trends", "summary", "last_10_days", summary_for_ai)
    return result


@app.get('/api/job-posting-list')
def job_posting_list():
    df = recent_job_postings()
    # Convert dates to a clean string format (YYYY-MM-DD) so they don't look like random epoch numbers
    df['posted_date'] = pd.to_datetime(df['posted_date']).dt.strftime('%Y-%m-%d')
    # Use to_json to safely serialize Pandas data and NaNs
    result = json.loads(df.to_json(orient='records'))

    save_dashboard_data("recent_market_trends", "recent_job_postings", "last_10_days", result)
    return result

@app.get("/api/get-top-locations")
def get_top_locations():
    location = recenttopLocations()
    top_4 = location.iloc[:4][:]

    top_4 = top_4.rename(columns={"location":"name","count":"value"})
    data = top_4.to_dict(orient='records')

    # Save before the chart colours are added; the AI does not need them.
    save_dashboard_data("recent_market_trends", "top_locations", "last_10_days", top_4.to_dict(orient='records'))

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


# _________________________ Ask AI Endpoint ________________________

def fill_missing_dashboard_data():
    """
    app.state.dashboard_data only fills up as the dashboard pages call the API.
    If someone opens Ask AI first, load the default view of every page
    (all fields, current year, top 3 roles) so the AI has data to use.
    Each endpoint saves its own result into app.state.dashboard_data.
    """
    dashboard_data = app.state.dashboard_data
    current_year = datetime.now().year

    try:
        if not dashboard_data["pipeline"]:
            last_sync()

        if not dashboard_data["market_overview"]:
            get_data_for_jobtile('all')
            get_job_postings(JobpostingModel(year=current_year, field='all'))
            get_top_companies(TopCompanyModel(year=current_year, field='all'))
            get_top_roles('all')

        if not dashboard_data["comparative_analysis"]:
            top_roles = get_top_roles('all')

            top_three_roles = []
            for row in top_roles[:3]:
                top_three_roles.append(row['role'])

            if len(top_three_roles) >= 2:
                get_role_postings(RolesPostingsModel(roles=top_three_roles))
                get_common_skill(CommonSkillModal(roles=top_three_roles))
                get_linechart_data(LinechartData(selected_jobs=top_three_roles))

        if not dashboard_data["recent_market_trends"]:
            get_recent_trends()
            job_posting_list()
            get_top_locations()

    except Exception as error:
      
        logging.error(f"Could not load dashboard data for Ask AI: {error}")


@app.post('/api/chatwith_ai')
async def chatwith_ai(request: ChatModel):
    question = request.question.strip()
    if question == "":
        return {"error": "Please type a question."}

    await asyncio.to_thread(fill_missing_dashboard_data)

    dashboard_data = app.state.dashboard_data
    answer = await get_ai_response(question, dashboard_data, 'chat')
    return answer

if __name__ == '__main__':
    pass
