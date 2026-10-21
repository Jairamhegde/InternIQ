from datetime import datetime

from fastapi import APIRouter

from queries.analysis import (
    job_postings, topSkills, topLocations, current_year_postings, toproles,
    top_hiring_company
)
from backend.models import OverviewInsightsModel, JobpostingModel, TopCompanyModel
from backend.crud import get_ai_response
from backend.dashboard_state import save_dashboard_data

router = APIRouter(tags=["market_overview"])


@router.post('/top-companies')
def get_top_companies(request: TopCompanyModel):
    actual_field = None if request.field.lower() == 'all' else request.field
    top_companies = top_hiring_company(request.year, actual_field, request.month)
    result = top_companies.to_dict(orient='records')

    filter_key = f"year={request.year}, field={request.field}, month={request.month}"
    save_dashboard_data("market_overview", "top_hiring_companies", filter_key, result)
    return result


@router.post('/job-postings')
def get_job_postings(request: JobpostingModel):
    actual_field = None if request.field.lower() == 'all' else request.field
    data = job_postings(request.year, actual_field)
    result = data.to_dict(orient='records')

    filter_key = f"year={request.year}, field={request.field}"
    save_dashboard_data("market_overview", "monthly_job_postings", filter_key, result)
    return result


@router.post('/job-posting-card-insights')
async def get_job_posting_insights(request: OverviewInsightsModel):
    actual_field = None if request.field.lower() == 'all' else request.field
    data = job_postings(request.year, actual_field)
    data_dict = data.to_dict(orient='records')
    res = await get_ai_response(data_dict, request.tile_data, 'overview')
    return res


@router.get('/job-tiles')
def get_data_for_jobtile(field: str = 'all'):
    actual_field = None if field.lower() == 'all' else field

    skills_df = topSkills(field=actual_field)
    skill = skills_df.iloc[0]['name'] if not skills_df.empty else "N/A"
    top_skill_count = int(skills_df.iloc[0]['demand']) if not skills_df.empty else 0

    loc_df = topLocations(field=actual_field)
    location = loc_df.iloc[0]['location'] if not loc_df.empty else "N/A"
    top_loc_count = int(loc_df.iloc[0]['count']) if not loc_df.empty else 0

    roles_df = toproles(field=actual_field)
    top_role = roles_df.iloc[0]['role'] if not roles_df.empty else "N/A"
    top_role_count = int(roles_df.iloc[0]['volume']) if not roles_df.empty else 0

    year_posting = int(current_year_postings(datetime.now().year, field=actual_field))

    result = {
        "skill": skill,
        "skillCount": top_skill_count,

        "location": location,
        "locationCount": top_loc_count,
        "year_posting": f"{year_posting:,}",
        "role": top_role,
        "roleCount": top_role_count

    }

    save_dashboard_data("market_overview", "summary_tiles", f"field={field}", result)
    return result


@router.get('/top-role-table')
def get_top_roles(field: str = 'all', limit: int | None = None):
    actual_field = None if field.lower() == 'all' else field
    data = toproles(field=actual_field)
    if limit:
        data = data.head(limit)
    result = data.to_dict(orient='records')

    filter_key = f"field={field}" if not limit else f"field={field},limit={limit}"
    save_dashboard_data("market_overview", "top_roles", filter_key, result)
    return result


@router.get('/top-skills')
def get_top_skills(field: str = 'all', limit: int = 5):
    actual_field = None if field.lower() == 'all' else field
    data = topSkills(field=actual_field).head(limit)
    result = data.to_dict(orient='records')

    save_dashboard_data("market_overview", "top_skills", f"field={field}", result)
    return result
