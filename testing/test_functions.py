import pytest
from queries.analysis import (top_locations, top_skills, top_roles)
from queries.future_use import (roles, number_of_opportunities, common_skills_of_roles,
                                top_skills_of_role, job_count, opportunities_last_10_days, unique_skill_count, roles_trends)

import numpy as np
import pandas as pd
from extract.extractor import date_from_text
from datetime import datetime
from transform.transform_data import convert_salary, strip_salary, detect_currency, convert_to_inr


def test_top_skills():
    df = top_skills()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "name" in df.columns
    assert "demand" in df.columns


def test_top_locations():
    df = top_locations()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "location" in df.columns
    assert "count" in df.columns


def test_top_roles():
    df = roles()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "title" in df.columns
    assert "demand" in df.columns


def test_number_of_opportunities():
    count = number_of_opportunities()
    assert isinstance(count, np.int64)


def test_common_skills():
    df = common_skills_of_roles()
    assert isinstance(df, pd.DataFrame)
    assert "skill" in df.columns
    assert "role_count" in df.columns
    assert "total_occurrences" in df.columns


def test_top_skill_roles():
    df = top_skills_of_role(roles()['title'][0])
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "demand" in df.columns


def test_job_count():
    df = job_count(roles()['title'][0])
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "no_of_jobs" in df.columns


def test_role_trends():
    df = roles_trends()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "month" in df.columns
    assert "name" in df.columns
    assert "job_count" in df.columns
    assert "rank" in df.columns


def test_opportunities_10days():
    count = opportunities_last_10_days()
    assert isinstance(count, np.int64)


def test_unique_skill_count():
    df = unique_skill_count(roles()['title'][0])
    assert "skill" in df.columns
    assert "count" in df.columns


def test_date_from_text():
    assert date_from_text('today') == datetime.now().strftime("%Y-%m-%d")
    assert date_from_text('few hours ago') == datetime.now().strftime("%Y-%m-%d")


def test_convert_salary():
    assert convert_salary('₹ 2,00,000 - 3,00,000') == (200000, 300000)
    assert convert_salary('₹ 25,000 - 35,000 /month') == (300000, 420000)
    assert convert_salary("Unpaid") == (0, 0)
    assert convert_salary("Competitive Salary") == (0, 0)
