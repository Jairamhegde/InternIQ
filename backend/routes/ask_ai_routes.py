import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter

from backend.models import (
    ChatModel, JobpostingModel, TopCompanyModel, RolesPostingsModel,
    CommonSkillModel, LinechartData
)
from backend.crud import get_ai_response
from backend.dashboard_state import dashboard_data
from backend.routes.health_routes import last_sync
from backend.routes.market_overview_routes import (
    get_job_tiles, get_job_postings, get_top_companies, get_top_roles
)
from backend.routes.comparative_analysis_routes import (
    get_role_postings, get_common_skill, get_line_chart_data
)
from backend.routes.recent_trends_routes import (
    get_recent_trends, job_posting_list, get_top_locations
)

router = APIRouter(tags=["ask_ai"])


def fill_missing_dashboard_data():
    """Loads each page's default data when Ask AI is opened before the dashboard pages."""
    current_year = datetime.now().year

    try:
        if not dashboard_data["pipeline"]:
            last_sync()

        if not dashboard_data["market_overview"]:
            get_job_tiles('all')
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
                get_common_skill(CommonSkillModel(roles=top_three_roles))
                get_line_chart_data(LinechartData(selected_jobs=top_three_roles))

        if not dashboard_data["recent_market_trends"]:
            get_recent_trends()
            job_posting_list()
            get_top_locations()

    except Exception as error:
        logging.error(f"Could not load dashboard data for Ask AI: {error}")


@router.post('/chatwith_ai')
async def chat_with_ai(request: ChatModel):
    question = request.question.strip()
    if question == "":
        return {"error": "Please type a question."}

    await asyncio.to_thread(fill_missing_dashboard_data)

    answer = await get_ai_response(question, dashboard_data, 'chat')
    return answer
