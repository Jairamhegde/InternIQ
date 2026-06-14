import pytest
from queries.recent_market_trends import (Top_role,top_skill,total_opportunities)
import pandas as pd

def test_top_roles():
    df = Top_role()
    assert isinstance(df,pd.DataFrame)
    assert "title" in df.columns
    assert "posted_date" in df.columns


def test_top_skills():
    df = top_skill()
    assert isinstance(df,pd.DataFrame)
    assert "skill" in df.columns
    assert "skill_count" in df.columns

def test_total_opportunities():
    df = total_opportunities()
    assert isinstance(df,pd.DataFrame)
    assert "total_opportunities" in df.columns
