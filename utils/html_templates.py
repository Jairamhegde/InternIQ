"""
HTML Templates and Styling Constants for Streamlit Dashboard.
"""

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
.material-icons, .material-symbols-outlined { font-family: 'Material Icons' !important; }

.stApp {
    background-color: #080b14;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(99,102,241,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(34,211,238,0.07) 0%, transparent 55%);
}
.block-container { padding: 1.5rem 2.5rem !important; max-width: 1600px !important; }

h1 {
    font-size: 2rem !important; font-weight: 700 !important;
    background: linear-gradient(120deg, #e2e8f0, #6366f1);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px; padding-bottom: 0 !important;
}
h2, h3 { color: #e2e8f0 !important; font-weight: 600 !important; letter-spacing: -0.3px; }

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #13172a 0%, #1a1f35 100%);
    border: 1px solid rgba(99,102,241,0.25); border-radius: 16px;
    padding: 20px 22px !important; position: relative; overflow: hidden;
    transition: border-color 0.25s, box-shadow 0.25s;
}
[data-testid="stMetric"]:hover { border-color: rgba(99,102,241,0.55); box-shadow: 0 0 24px rgba(99,102,241,0.12); }
[data-testid="stMetric"]::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #6366f1, #22d3ee); border-radius: 16px 16px 0 0;
}
[data-testid="stMetricLabel"] p { font-size: 10px !important; font-weight: 600 !important; color: #64748b !important; text-transform: uppercase; letter-spacing: 1.2px; }
[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; font-size: 26px !important; font-weight: 600 !important; color: #f1f5f9 !important; }
[data-testid="stMetricDelta"] { font-size: 12px !important; color: #34d399 !important; }

div[data-testid="stPlotlyChart"] {
    background: linear-gradient(145deg, #0d1117, #131825) !important;
    border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 16px !important;
    padding: 8px !important; transition: border-color 0.25s;
}
div[data-testid="stPlotlyChart"]:hover { border-color: rgba(99,102,241,0.3) !important; }
div[data-testid="stPlotlyChart"] * { background: transparent !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #0d0f14 !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}
section[data-testid="stSidebar"] .block-container { padding: 0 !important; }

/* Nav buttons */
div.stButton > button {
    background: transparent !important;
    border: none !important;
    color: #4a5272 !important;
    border-radius: 8px !important;
    font-size: 13.5px !important;
    font-weight: 400 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 9px 12px !important;
    transition: all 0.18s ease !important;
    text-align: left !important;
    margin-bottom: 2px;
    width: 100%;
    letter-spacing: 0;
}
div.stButton > button:hover {
    background: #161a26 !important;
    color: #c8d0e8 !important;
    transform: none !important;
}
div.stButton > button:focus,
div.stButton > button:active {
    background: #131827 !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stMarkdownContainer"] h3 { padding-left: 12px; border-left: 3px solid #6366f1; color: #e2e8f0 !important; }
[data-testid="stDataFrame"] { background: #0d1117 !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 12px !important; overflow: hidden; }
[data-testid="stSelectbox"] > div, [data-testid="stMultiSelect"] > div { background: #13172a !important; border: 1px solid rgba(99,102,241,0.25) !important; border-radius: 10px !important; color: #e2e8f0 !important; }
[data-testid="stProgress"] > div > div { background: linear-gradient(90deg, #6366f1, #22d3ee) !important; border-radius: 99px; }
[data-testid="stExpander"] { background: #0d1117 !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 12px !important; }

hr { border-color: rgba(255,255,255,0.06) !important; }
[data-testid="stCaptionContainer"] { color: #475569 !important; font-size: 12px !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0c0f1e; }
::-webkit-scrollbar-thumb { background: #2d3556; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #6366f1; }
</style>
"""

BRAND_HEADER_HTML = """
<div style="padding:28px 20px 24px;font-family:'DM Sans',sans-serif">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:32px">
        <div style="width:30px;height:30px;background:#4f8ef7;border-radius:8px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:13px;font-weight:700;color:#fff;flex-shrink:0">IQ</div>
        <span style="font-size:15px;font-weight:500;color:#fff;font-family:'DM Sans',sans-serif">
            Intern<span style="color:#4f8ef7">IQ</span>
        </span>
    </div>
    <p style="font-size:10px;font-weight:500;letter-spacing:0.12em;color:#2e3450;
              text-transform:uppercase;margin:0 0 6px;padding:0 4px">Analytics</p>
</div>
"""

COMPARE_DIVIDER_HTML = """
<div style="padding:0 20px;font-family:'DM Sans',sans-serif">
    <div style="height:0.5px;background:#161a24;margin:10px 0 14px"></div>
    <p style="font-size:10px;font-weight:500;letter-spacing:0.12em;color:#2e3450;
              text-transform:uppercase;margin:0 0 6px;padding:0 4px">Compare</p>
</div>
"""

PAGE_SUBTITLE_HTML = """
<p style='color:#64748b;font-size:14px;margin-top:-8px;margin-bottom:24px'>
Real-time insights from scraped job postings</p>
"""

CROSS_FUNCTIONAL_SUBTEXT_HTML = """
<p style='color:#64748b;font-size:13px;margin-top:-6px'>
Skills required across multiple top roles</p>
"""

MOST_IN_DEMAND_SKILLS_HEADER = "<h3>Most In-Demand Skills</h3>"

SKILL_PRIORITY_SUBTEXT_HTML = """
<p style='color:#64748b;font-size:11px;font-weight:600;text-transform:uppercase;
letter-spacing:1px;margin-bottom:6px'>Skill Priority</p>
"""

MUST_HAVE_SKILLS_HEADER_HTML = """
<div style='background:#0d1117;border:1px solid rgba(99,102,241,0.2);
border-radius:12px;padding:18px 22px'>
<p style='color:#6366f1;font-weight:600;font-size:12px;text-transform:uppercase;
letter-spacing:1px;margin-bottom:12px'>Must-Have Skills</p>
"""

EMERGING_SKILLS_HEADER_HTML = """
<div style='background:#0d1117;border:1px solid rgba(52,211,153,0.2);
border-radius:12px;padding:18px 22px'>
<p style='color:#34d399;font-weight:600;font-size:12px;text-transform:uppercase;
letter-spacing:1px;margin-bottom:12px'>Emerging Skills</p>
"""

CLOSE_DIV_HTML = "</div>"

BR_HTML = "<br>"


def insight_card(icon, label, label_color, value, sub, sub_color, bg_color):
    return f"""
    <div style="background:#13172a;border:1px solid rgba(99,102,241,0.2);border-radius:14px;
                padding:18px 20px;display:flex;align-items:flex-start;gap:14px">
      <div style="width:42px;height:42px;border-radius:50%;background:{bg_color};
                  display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">{icon}</div>
      <div>
        <p style="color:{label_color};font-size:12px;font-weight:600;letter-spacing:.6px;
                  text-transform:uppercase;margin:0 0 4px">{label}</p>
        <p style="color:#fff;font-size:18px;font-weight:700;margin:0 0 4px">{value}</p>
        <p style="color:{sub_color};font-size:13px;margin:0">{sub}</p>
      </div>
    </div>"""


def key_insight_card(text):
    return f"""
    <div style="background:#13172a;border:1px solid rgba(99,102,241,0.15);border-radius:14px;
                padding:18px 20px;display:flex;align-items:flex-start;gap:14px">
      <div style="width:42px;height:42px;border-radius:50%;background:#2a1f00;
                  display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0"></div>
      <div>
        <p style="color:#f59e0b;font-size:13px;font-weight:700;letter-spacing:.5px;
                  text-transform:uppercase;margin:0 0 6px">Key Insight</p>
        <p style="color:#cbd5e1;font-size:14px;line-height:1.6;margin:0">{text}</p>
      </div>
    </div>"""


def insights_section(cards_html, insight_html):
    grid = "".join(cards_html)
    return f"""
    <div style="background:#0d1117;border-radius:16px;padding:28px;margin-top:16px">
      <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px;
                  border-left:3px solid #6366f1;padding-left:14px">
        <div style="background:#1e1b4b;border-radius:10px;width:42px;height:42px;
                    display:flex;align-items:center;justify-content:center;font-size:20px"></div>
        <p style="color:#fff;font-size:22px;font-weight:600;margin:0">Insights received</p>
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:16px">
        {grid}
      </div>
      {insight_html}
    </div>"""


def get_market_analysis_html(toprole):
    title0 = toprole['title'][0].capitalize()
    count0 = toprole['job_count'][0]
    title1 = toprole['title'][1].capitalize()
    count1 = toprole['job_count'][1]
    title2 = toprole['title'][2]
    count2 = toprole['job_count'][2]
    title3 = toprole['title'][3].capitalize()
    count3 = toprole['job_count'][3]
    title4 = toprole['title'][4].capitalize()
    count4 = toprole['job_count'][4]
    
    return f"""<div style='
            background:linear-gradient(135deg,#13172a,#1a1f35);
            border:1px solid rgba(99,102,241,0.2);
            border-radius:16px;padding:24px 28px;font-size:18px'>
            <h3>Market Analysis</h3><br>
            <p style="font-size:20px">
            The current hiring trend is led by
            <b style='color:#6366f1'>{title0}</b>
            with <b style='color:#34d399'>{count0}</b> openings,
            followed by <b style="color:#6366f1;">{title1}</b>
            (<b style='color:#34d399'>{count1} openings</b>),
            <b style="color:#6366f1">{title2}</b>
            (<b style='color:#34d399'>{count2} openings</b>),
            {title3} ({count3} openings), and
            <b style="color:#6366f1">{title4}</b>
            (<b style='color:#34d399'>{count4} openings</b>),
            highlighting strong demand for modern software and data-focused roles across the tech industry.
            </p></div>
        """


def get_skill_market_analysis_html(topSkill_df):
    skill0 = topSkill_df['skill'][0].capitalize()
    skill1 = topSkill_df['skill'][1].capitalize()
    return f"""<div style='
            background:linear-gradient(135deg,#13172a,#1a1f35);
            border:1px solid rgba(99,102,241,0.2);
            border-radius:16px;padding:24px 28px;font-size:18px'>
            <h3>Skill Market Analysis</h3><br>
            <p>The current market trend is dominated by strong demand for
            <b style='color:#6366f1'>{skill0}</b> and
            <b style='color:#6366f1'>{skill1}</b></p></div>
        """
