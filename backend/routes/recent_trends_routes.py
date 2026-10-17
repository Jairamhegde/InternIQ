import json

import pandas as pd
from fastapi import APIRouter

from queries.recent_market_trends import (
    Top_role, top_skill, total_opportunities, average_salary,
    recenttopLocations, previous_total_opportunities, recent_job_postings
)
from backend.dashboard_state import save_dashboard_data

router = APIRouter(tags=["recent_trends"])


@router.get("/recent-market-trend")
def get_recent_trends():
    df_top_role = Top_role()
    df_top_skill = top_skill()
    df_opportunities = total_opportunities()
    df_top_location = recenttopLocations()
    pre_total_opp = previous_total_opportunities()

    top_role = df_top_role.iloc[0]["title"] if not df_top_role.empty else None
    top_role_count = int(df_top_role.iloc[0]["job_count"]) if not df_top_role.empty else 0

    avg_sal = None
    if top_role:
        df_avg_sal = average_salary(top_role)
        if not df_avg_sal.empty and pd.notnull(df_avg_sal.iloc[0]['average']):
            avg_sal = float(df_avg_sal.iloc[0]['average'])

    top_skill_name = df_top_skill.iloc[0]["skill"]
    top_skill_count = int(df_top_skill.iloc[0]["skill_count"])

    total_opportunity = int(df_opportunities.iloc[0]["total_opportunities"])

    top_location = df_top_location.iloc[0]['location']
    top_location_count = int(df_top_location.iloc[0]['count'])

    chart_data = df_top_role.rename(columns={"title": "role", "job_count": "volume"}).to_dict(orient='records')

    prev_opportunity = int(pre_total_opp.iloc[0]["total_opportunities"]) if not pre_total_opp.empty else 0

    if prev_opportunity > 0:
        increment = round(((total_opportunity - prev_opportunity) / prev_opportunity) * 100, 2)
    else:
        increment = 100.0 if total_opportunity > 0 else 0.0

    result = {
        "role": [top_role, top_role_count],
        "skill": [top_skill_name, top_skill_count],
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
        "top_skill": {"skill": top_skill_name, "mentions": top_skill_count},
        "top_location": {"location": top_location, "postings": top_location_count},
        "average_stipend_of_top_role": avg_sal,
        "postings_per_role": chart_data,
    }
    save_dashboard_data("recent_market_trends", "summary", "last_10_days", summary_for_ai)
    return result


@router.get('/job-posting-list')
def job_posting_list():
    df = recent_job_postings()
    # Convert dates to a clean string format (YYYY-MM-DD) so they don't look like random epoch numbers
    df['posted_date'] = pd.to_datetime(df['posted_date']).dt.strftime('%Y-%m-%d')
    # Use to_json to safely serialize Pandas data and NaNs
    result = json.loads(df.to_json(orient='records'))

    save_dashboard_data("recent_market_trends", "recent_job_postings", "last_10_days", result)
    return result


@router.get("/get-top-locations")
def get_top_locations():
    location = recenttopLocations()
    top_4 = location.iloc[:4][:]

    top_4 = top_4.rename(columns={"location": "name", "count": "value"})
    data = top_4.to_dict(orient='records')

    # Save before the chart colours are added; the AI does not need them.
    save_dashboard_data("recent_market_trends", "top_locations", "last_10_days", top_4.to_dict(orient='records'))

    COLORS = ['#f43f5e', '#f97316', '#f59e0b', '#facc15']
    for i, j in enumerate(data):
        j['fill'] = COLORS[i % len(COLORS)]

    return data
