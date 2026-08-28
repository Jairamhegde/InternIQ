import pytest
from queries.analysis import (topLocations, topSkills, roles,
                              noOfopportunities, commonSkills,
                              TopSkillsOfRole, jobCount, roles_trends,
                              OPPORTUNITIES, uniqueSkillCount)
import numpy as np
import pandas as pd
from extract.extractor import dateFromtext 
from datetime import datetime
from transform.transformData import convertSalary,stripedSal,detect_currency,currencymap

def test_top_skills():
    df = topSkills()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "name" in df.columns
    assert "demand" in df.columns


def test_top_locations():
    df = topLocations()
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


def test_noof_opportunities():
    count = noOfopportunities()
    assert isinstance(count, np.int64)


def test_common_skills():
    df = commonSkills()
    assert isinstance(df, pd.DataFrame)
    assert "skill" in df.columns
    assert "role_count" in df.columns
    assert "total_occurrences" in df.columns


def test_topSkill_roles():
    df = TopSkillsOfRole(roles()['title'][0])   
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "demand" in df.columns


def test_jobCount():
    df = jobCount(roles()['title'][0])          
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "no_of_jobs" in df.columns


def test_role_trends():
    df = roles_trends()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "month" in df.columns
    assert "name" in df.columns
    assert "jobcount" in df.columns
    assert "rank" in df.columns


def test_opportunities_10days():
    count = OPPORTUNITIES()
    assert isinstance(count, np.int64)


def test_unique_skill_count():
    df = uniqueSkillCount(roles()['title'][0])  
    assert "skill" in df.columns
    assert "count" in df.columns



#________________________________________________________________

def test_DateFromText():
    assert dateFromtext('today') == datetime.now().strftime("%Y-%m-%d")
    assert dateFromtext('few hours ago') == datetime.now().strftime("%Y-%m-%d")

def test_convertSalary():
    assert convertSalary('₹ 2,00,000 - 3,00,000') == (200000, 300000)
    assert convertSalary('₹ 25,000 - 35,000 /month') == (300000, 420000)


if __name__ == "__main__":
    pass

    