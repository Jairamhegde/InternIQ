from fastapi import APIRouter

from queries.role_specific_analysis import role_details

router = APIRouter(tags=["role_details"])


@router.get('/role-details')
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
