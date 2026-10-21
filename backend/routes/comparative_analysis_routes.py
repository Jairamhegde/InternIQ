from fastapi import APIRouter

from queries.analysis import top_roles
from queries.comparative_analysis import (
    compare_role_trend, get_skill_percentages, average_salary_by_role
)
from backend.models import (
    RolesPostingsModel, CommonSkillModel, ComparativeInsightsModel, LinechartData
)
from backend.crud import get_ai_response
from backend.dashboard_state import save_dashboard_data

router = APIRouter(tags=["comparative_analysis"])


@router.post('/get-role-posting')
def get_role_postings(request: RolesPostingsModel):
    role_list = [role.lower() for role in request.roles]
    data = top_roles()
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


@router.post('/common-skill')
def get_common_skill(request: CommonSkillModel):
    df = get_skill_percentages(request.roles)
    pivot_df = df.pivot(index='skill', columns='title', values='percentage').reset_index().fillna(0)
    result = pivot_df.to_dict(orient='records')

    filter_key = "roles=" + ", ".join(request.roles)
    save_dashboard_data("comparative_analysis", "skill_share_percent_per_role", filter_key, result)
    return result


@router.post('/get-comparative-insights')
async def get_comparative_insights(request: ComparativeInsightsModel):
    roles_frequency = request.role_frequency
    common_skills = request.common_skill
    insights = await get_ai_response(roles_frequency, common_skills, 'comparison')
    return insights


@router.post('/get-linechart-data')
def get_line_chart_data(request: LinechartData):
    if not request.selected_jobs:
        return []

    df = compare_role_trend(*request.selected_jobs)

    if df is None or df.empty:
        return []

    result = df.to_dict(orient='records')

    filter_key = "roles=" + ", ".join(request.selected_jobs)
    save_dashboard_data("comparative_analysis", "monthly_postings_per_role", filter_key, result)
    return result
