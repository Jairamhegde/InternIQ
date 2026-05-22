import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from queries.analysis import roles, noOfopportunities, roles_trends, TopSkillsOfRole, jobCount, topSkills, topLocations, commonSkills, last_scraped_time
from queries.recent_market_trends import Top_role,top_skill,total_opportunities
import pandas as pd
import plotly.io as pio

pio.templates["mytheme"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit", color="#cbd5e1"),
        colorway=["#6366f1", "#22d3ee", "#f472b6", "#34d399", "#fb923c", "#a78bfa"],
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)"),
    )
)
pio.templates.default = "mytheme"

st.set_page_config(
    page_title="Job Market Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}
.material-icons,
.material-symbols-outlined {
    font-family: 'Material Icons' !important;
}

/* ── Base ───────────────────────────────────── */
.stApp {
    background-color: #080b14;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(99,102,241,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(34,211,238,0.07) 0%, transparent 55%);
}

.block-container {
    padding: 1.5rem 2.5rem !important;
    max-width: 1600px !important;
}

/* ── Headings ───────────────────────────────── */
h1 {
    font-size: 2rem !important;
    font-weight: 700 !important;
    background: linear-gradient(120deg, #e2e8f0, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    padding-bottom: 0 !important;
}

h2, h3 {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    letter-spacing: -0.3px;
}

/* ── Metric Cards ───────────────────────────── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #13172a 0%, #1a1f35 100%);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px;
    padding: 20px 22px !important;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s, box-shadow 0.25s;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(99,102,241,0.55);
    box-shadow: 0 0 24px rgba(99,102,241,0.12);
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #22d3ee);
    border-radius: 16px 16px 0 0;
}

[data-testid="stMetricLabel"] p {
    font-size: 10px !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}

[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 26px !important;
    font-weight: 600 !important;
    color: #f1f5f9 !important;
}

[data-testid="stMetricDelta"] {
    font-size: 12px !important;
    color: #34d399 !important;
}

/* ── Chart Containers ───────────────────────── */
div[data-testid="stPlotlyChart"] {
    background: linear-gradient(145deg, #0d1117, #131825) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 16px !important;
    padding: 8px !important;
    transition: border-color 0.25s;
}
div[data-testid="stPlotlyChart"]:hover {
    border-color: rgba(99,102,241,0.3) !important;
}
div[data-testid="stPlotlyChart"] * {
    background: transparent !important;
}

/* ── Sidebar ────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #0c0f1e !important;
    border-right: 1px solid rgba(255,255,255,0.06);
    padding-top: 1.5rem;
}
section[data-testid="stSidebar"] .block-container {
    padding: 0 1rem !important;
}

/* ── Sidebar Buttons ────────────────────────── */
div.stButton > button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    color: #94a3b8 !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    transition: all 0.2s ease !important;
    text-align: left !important;
    margin-bottom: 4px;
    width: 100%;
}
div.stButton > button:hover {
    background: rgba(99,102,241,0.12) !important;
    border-color: rgba(99,102,241,0.4) !important;
    color: #e2e8f0 !important;
    transform: translateX(3px);
}

/* ── Subheader Accent ───────────────────────── */
[data-testid="stMarkdownContainer"] h3 {
    padding-left: 12px;
    border-left: 3px solid #6366f1;
    color: #e2e8f0 !important;
}

/* ── DataFrames ─────────────────────────────── */
[data-testid="stDataFrame"] {
    background: #0d1117 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* ── Selectbox & Multiselect ────────────────── */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: #13172a !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── Progress bar ───────────────────────────── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #6366f1, #22d3ee) !important;
    border-radius: 99px;
}

/* ── Expander ───────────────────────────────── */
[data-testid="stExpander"] {
    background: #0d1117 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}

/* ── Divider & Caption ──────────────────────── */
hr { border-color: rgba(255,255,255,0.06) !important; }
[data-testid="stCaptionContainer"] { color: #475569 !important; font-size: 12px !important; }

/* ── Scrollbar ──────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0c0f1e; }
::-webkit-scrollbar-thumb { background: #2d3556; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #6366f1; }
</style>
"""

def load_dashboard():
    st.markdown(STYLES, unsafe_allow_html=True)

    def load_all_data():
        return {
            'roles': roles(),
            'skills': topSkills(),
            'locations': topLocations(),
            'common_roles': commonSkills(),
            'opportunity': noOfopportunities()
        }

    data = load_all_data()
    df_roles = data['roles']
    df_skills = data['skills']
    df_locations = data['locations']
    cross_functional_skills = data['common_roles']

    with st.sidebar:
        st.markdown(
            "<div style='padding:0 4px 20px'>"
            "<p style='font-size:11px;font-weight:600;color:#475569;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:12px'>Navigation</p>"
            "</div>",
            unsafe_allow_html=True
        )
        pages = ["Overall Market Trends", "Recent Market Trend", "Role-Specific Analysis", "Comparative Analysis", "Trends Over Time"]
        if "page" not in st.session_state:
            st.session_state.page = pages[0]
       
        for pg in  pages:
            if st.button(f"{pg}", use_container_width=True):
                st.session_state.page = pg
        page = st.session_state.page
        total_job_count = data['opportunity']

    # ── Page Header ──────────────────────────────
    st.markdown("# Internship Job Market Intelligence")
    st.markdown(
        "<p style='color:#64748b;font-size:14px;margin-top:-8px;margin-bottom:24px'>"
        "Real-time insights from scraped job postings</p>",
        unsafe_allow_html=True
    )

    # ════════════════════════════════════════════
    # PAGE: OVERALL MARKET TRENDS
    # ════════════════════════════════════════════
    if page == "Overall Market Trends":
        st.markdown("### Market Overview")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Opportunities Tracked", f"{total_job_count:,}", "Active Postings")
        with col2:
            top_role = df_roles.iloc[0]['J_title']
            st.metric("Top Role", top_role[:20] + "…" if len(top_role) > 20 else top_role,
                      f"{df_roles.iloc[0]['demand']} jobs")
        with col3:
            st.metric("Most Demanded Skill", df_skills.iloc[0]['name'],
                      f"{df_skills.iloc[0]['demand']} mentions")
        with col4:
            st.metric("Top Location", df_locations.iloc[0]['location'],
                      f"{df_locations.iloc[0]['count']} jobs")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Market Demand Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Top 10 In-Demand Roles**")
            fig_roles = px.bar(
                df_roles, x='demand', y='J_title', orientation='h', text='demand',
                labels={'demand': 'Job Postings', 'J_title': ''}
            )
            fig_roles.update_traces(
                marker=dict(color=df_roles['demand'], colorscale=[[0, '#312e81'], [1, '#6366f1']]),
                textposition='outside', textfont=dict(color='#94a3b8', size=11)
            )
            fig_roles.update_layout(
                height=480, showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(l=10, r=50, t=10, b=10),
            )
            st.plotly_chart(fig_roles, use_container_width=True)

        with col2:
            st.markdown("**Top 10 In-Demand Skills**")
            fig_skills = px.bar(
                df_skills, x='demand', y='name', orientation='h',
                color='demand', color_continuous_scale=[[0, '#134e4a'], [1, '#34d399']],
                text='demand', labels={'demand': 'Mentions', 'name': ''}
            )
            fig_skills.update_traces(textposition='outside', textfont=dict(color='#94a3b8', size=11))
            fig_skills.update_layout(
                height=480, showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(l=10, r=50, t=10, b=10),
            )
            st.plotly_chart(fig_skills, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("###Geographic Distribution")

        col1, col2 = st.columns([1, 1])

        with col1:
            fig_locations = px.bar(
                df_locations, x='location', y='count',
                color='count', color_continuous_scale=[[0, '#431407'], [1, '#fb923c']],
                text='count', labels={'count': 'Jobs', 'location': ''}
            )
            fig_locations.update_traces(texttemplate='%{text}', textposition='outside',
                                        textfont=dict(color='#94a3b8', size=11))
            fig_locations.update_layout(
                title=dict(text="Top 10 Job Locations", font=dict(color='#94a3b8', size=13)),
                height=380, showlegend=False, xaxis_tickangle=-40,
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig_locations, use_container_width=True)

        with col2:
            fig_pie = px.pie(
                df_roles.head(8), values='demand', names='J_title', hole=0.55,
                title='Market Share by Top Roles',
                color_discrete_sequence=['#6366f1','#818cf8','#22d3ee','#34d399',
                                         '#f472b6','#fb923c','#a78bfa','#38bdf8']
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label',
                                  textfont=dict(size=11))
            fig_pie.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10),
                                  title=dict(font=dict(color='#94a3b8', size=13)))
            st.plotly_chart(fig_pie, use_container_width=True)

        if not cross_functional_skills.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Cross-Functional Skills")
            st.markdown(
                "<p style='color:#64748b;font-size:13px;margin-top:-6px'>Skills required across multiple top roles</p>",
                unsafe_allow_html=True
            )
            fig_common = px.bar(
                cross_functional_skills.head(15), x='total_occurrences', y='skill', orientation='h',
                text='total_occurrences',
                labels={'total_occurrences': 'Total Occurrences', 'skill': ''}
            )
            fig_common.update_traces(
                texttemplate='%{text}', textposition='outside',
                textfont=dict(color='#94a3b8', size=11),
                marker=dict(color=cross_functional_skills['role_count'], colorscale=[[0,'#1e1b4b'],[1,'#a78bfa']])
            )
            fig_common.update_layout(
                height=480, yaxis={'categoryorder': 'total ascending'},
                margin=dict(l=10, r=50, t=10, b=10),
            )
            st.plotly_chart(fig_common, use_container_width=True)

        with st.expander("View Detailed Data Tables"):
            tab1, tab2, tab3 = st.tabs(["Roles", "Skills", "Locations"])
            with tab1:
                st.dataframe(df_roles, use_container_width=True, height=380)
            with tab2:
                st.dataframe(df_skills, use_container_width=True, height=380)
            with tab3:
                st.dataframe(df_locations, use_container_width=True, height=380)

    # ════════════════════════════════════════════
    # PAGE: RECENT MARKET TREND
    # ════════════════════════════════════════════
    elif page == "Recent Market Trend":
        
        toprole = Top_role()
        topSkill = top_skill()
        total_opportunity = total_opportunities()
        
        st.markdown("### Last 10 Days Market Trends")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Opportunities", total_opportunity['total_opportunities'])
        with col2:
            st.metric("Demanding Skill",topSkill['skill'][0])
        with col3:
            st.metric("Demanding Role",toprole['J_title'][0])

        # chart for top roles------------------------------------
        chart = px.bar(toprole,x="J_title",y="job_count",
                       text='job_count',
                       labels={"job_count":"Number of jobs",
                               "J_title":"Job title"},
                        color='job_count',
                        color_continuous_scale=[[0,'#1e1b4b'],[1,'#6366f1']])
        chart.update_traces( textposition='outside')

        #description---------------------------------------------
        st.plotly_chart(chart,use_container_width=True)

        st.markdown(f"""<div style='
                    background:linear-gradient(135deg,#13172a,#1a1f35);
                    border:1px solid rgba(99,102,241,0.2);
                    border-radius:16px;padding:24px 28px;
                    font-size:18px'>
                    <h3>Market Analysis</h3><br>
                    <p style="font-size:20px">
                    The current hiring trend is led by <b style='color:#6366f1'>{toprole['J_title'][0].capitalize()}</b> with <b style='color:#34d399'>{toprole['job_count'][0]}</b> openings, 
                    followed by <b style="color:#6366f1;">{toprole['J_title'][1].capitalize()}</b> (<b style='color:#34d399'>{toprole['job_count'][1]} openings</b>), <b style="color:#6366f1">{toprole['J_title'][2]
                    }</b> (<b style='color:#34d399'>{toprole['job_count'][2]} openings</b>),{toprole['J_title'][3].capitalize()} ({toprole['job_count'][3]} openings), and <b style="color:#6366f1">{toprole['J_title'][4].capitalize()}</b> (<b style='color:#34d399'>{toprole['job_count'][4]} openings</b>), highlighting 
                    strong demand for modern software and data-focused roles across the tech industry.</p></div>
                """,unsafe_allow_html=True)
        
        st.markdown('<br>',unsafe_allow_html=True)

        # Skills section------------------------------------------
        st.markdown("<h3 >Most In-Demand Skills</h3>",unsafe_allow_html=True)
        st.markdown('<br>',unsafe_allow_html=True)
        skill_chart = px.bar(
            topSkill,
            x="skill",
            y="skill_count",
            labels={
                "skill":"Skill",
                "skill_count":"Mentions"
            },
            color = "skill_count",
            color_continuous_scale=[[0,"#0f2a10"],[1,"#52c558"]]

        )
        st.plotly_chart(skill_chart,use_container_width=True)

        st.markdown(f"""<div style='
                background:linear-gradient(135deg,#13172a,#1a1f35);
                border:1px solid rgba(99,102,241,0.2);
                border-radius:16px;padding:24px 28px;
                font-size:18px'>
                <h3>Skill Market Analysis</h3><br>
                <p>
                The current market trend is dominated by strong demand for <b style='color:#6366f1'>{topSkill['skill'][0].capitalize()}</b> 
                and <b style='color:#6366f1'>{topSkill['skill'][1].capitalize()}</b></p></div>
            """,unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        

    # ════════════════════════════════════════════
    # PAGE: ROLE-SPECIFIC ANALYSIS
    # ════════════════════════════════════════════
    elif page == "Role-Specific Analysis":
        st.markdown("### Role-Specific Analysis")

        col1, col2 = st.columns([2, 1])
        with col1:
            selected_role = st.selectbox("Select a role:", df_roles['J_title'].tolist(), key="role_selector")
        with col2:
            role_rank = df_roles[df_roles['J_title'] == selected_role].index[0] + 1
            st.metric("Role Ranking", f"#{role_rank}", f"out of {len(df_roles)}")

        df_role_skills = TopSkillsOfRole(selected_role)
        df_job_count = jobCount(selected_role)
        total_jobs = df_job_count.iloc[0]['no_of_jobs']

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Openings", f"{total_jobs}", "Active Positions")
        with col2:
            st.metric("Required Skills", f"{len(df_role_skills)}", "Unique skills")
        with col3:
            avg_skills = df_role_skills['demand'].mean()
            st.metric("Avg. Skill Mentions", f"{avg_skills:.0f}", "per skill")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Skills Breakdown")

        col1, col2 = st.columns([2, 1])
        with col1:
            fig_role_skills = px.bar(
                df_role_skills, x='demand', y='name', orientation='h',
                color='demand', color_continuous_scale=[[0,'#134e4a'],[1,'#34d399']],
                text='demand', labels={'demand': 'Frequency', 'name': ''}
            )
            fig_role_skills.update_traces(texttemplate='%{text}', textposition='outside',
                                          textfont=dict(color='#94a3b8', size=11))
            fig_role_skills.update_layout(
                title=dict(text=f"Skills for {selected_role}", font=dict(color='#94a3b8', size=13)),
                height=580, showlegend=False, yaxis={'categoryorder': 'total ascending'},
                margin=dict(l=10, r=50, t=40, b=10),
            )
            st.plotly_chart(fig_role_skills, use_container_width=True)

        with col2:
            fig_skill_pie = px.pie(
                df_role_skills.head(8), values='demand', names='name',
                title='Top 8 Skills',
                color_discrete_sequence=['#6366f1','#818cf8','#22d3ee','#34d399',
                                         '#f472b6','#fb923c','#a78bfa','#38bdf8']
            )
            fig_skill_pie.update_traces(textposition='inside', textinfo='percent+label',
                                        textfont=dict(size=10))
            fig_skill_pie.update_layout(height=300, margin=dict(l=0, r=0, t=35, b=0),
                                        title=dict(font=dict(color='#94a3b8', size=13)))
            st.plotly_chart(fig_skill_pie, use_container_width=True)

            if len(df_role_skills) > 0:
                st.markdown(
                    "<p style='color:#64748b;font-size:11px;font-weight:600;text-transform:uppercase;"
                    "letter-spacing:1px;margin-bottom:6px'>Skill Priority</p>",
                    unsafe_allow_html=True
                )
                top_skill_pct = (df_role_skills.iloc[0]['demand'] / df_role_skills['demand'].sum()) * 100
                st.progress(top_skill_pct / 100)
                st.caption(f"**{df_role_skills.iloc[0]['name']}** in {top_skill_pct:.1f}% of requirements")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Career Insights")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                "<div style='background:#0d1117;border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:18px 22px'>"
                "<p style='color:#6366f1;font-weight:600;font-size:12px;text-transform:uppercase;"
                "letter-spacing:1px;margin-bottom:12px'>Must-Have Skills</p>",
                unsafe_allow_html=True
            )
            for idx, row in df_role_skills.head(3).iterrows():
                pct = (row['demand'] / total_jobs) * 100
                st.markdown(f"**{idx+1}. {row['name']}** — Required in {pct:.0f}% of postings")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(
                "<div style='background:#0d1117;border:1px solid rgba(52,211,153,0.2);border-radius:12px;padding:18px 22px'>"
                "<p style='color:#34d399;font-weight:600;font-size:12px;text-transform:uppercase;"
                "letter-spacing:1px;margin-bottom:12px'>Emerging Skills</p>",
                unsafe_allow_html=True
            )
            if len(df_role_skills) > 5:
                for _, row in df_role_skills.tail(3).iterrows():
                    st.markdown(f"• **{row['name']}** — {row['demand']} mentions")
            else:
                st.info("Not enough data for emerging skills analysis")
            st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("View Complete Skills Data"):
            st.dataframe(df_role_skills, use_container_width=True, height=380)

    # ════════════════════════════════════════════
    # PAGE: COMPARATIVE ANALYSIS
    # ════════════════════════════════════════════
    elif page == "Comparative Analysis":
        st.markdown("### Comparative Role Analysis")
        st.markdown(
            "<p style='color:#64748b;font-size:13px;margin-top:-6px'>Compare roles side by side</p>",
            unsafe_allow_html=True
        )

        selected_roles = st.multiselect(
            "Select 2–4 roles to compare:",
            df_roles['J_title'].tolist(),
            default=df_roles['J_title'].tolist()[:3],
            max_selections=4
        )

        if len(selected_roles) >= 2:
            comparison_data = []
            for role in selected_roles:
                job_count = jobCount(role).iloc[0]['no_of_jobs']
                skills = TopSkillsOfRole(role)
                comparison_data.append({
                    'Role': role, 'Jobs': job_count,
                    'Unique Skills': len(skills),
                    'Avg Skill Demand': round(skills['demand'].mean(), 1) if len(skills) > 0 else 0
                })
            df_comparison = pd.DataFrame(comparison_data)

            col1, col2 = st.columns(2)
            with col1:
                fig_comp_jobs = px.bar(
                    df_comparison, x='Role', y='Jobs',
                    color='Jobs', color_continuous_scale=[[0,'#1e1b4b'],[1,'#6366f1']],
                    text='Jobs', title="Job Openings Comparison"
                )
                fig_comp_jobs.update_traces(texttemplate='%{text}', textposition='outside',
                                            textfont=dict(color='#94a3b8', size=11))
                fig_comp_jobs.update_layout(height=380, showlegend=False,
                                            margin=dict(l=10, r=10, t=40, b=10),
                                            title=dict(font=dict(color='#94a3b8', size=13)))
                st.plotly_chart(fig_comp_jobs, use_container_width=True)

            with col2:
                fig_comp_skills = px.bar(
                    df_comparison, x='Role', y='Unique Skills',
                    color='Unique Skills', color_continuous_scale=[[0,'#134e4a'],[1,'#34d399']],
                    text='Unique Skills', title="Unique Skills Required"
                )
                fig_comp_skills.update_traces(texttemplate='%{text}', textposition='outside',
                                              textfont=dict(color='#94a3b8', size=11))
                fig_comp_skills.update_layout(height=380, showlegend=False,
                                              margin=dict(l=10, r=10, t=40, b=10),
                                              title=dict(font=dict(color='#94a3b8', size=13)))
                st.plotly_chart(fig_comp_skills, use_container_width=True)

            import numpy as np

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Skills Overlap Analysis")

            all_skills = set()
            role_skills_dict = {}
            for role in selected_roles:
                skills_df = TopSkillsOfRole(role)
                role_skills_dict[role] = set(skills_df['name'].tolist())
                all_skills.update(skills_df['name'].tolist())

            matrix_data = []
            for skill in sorted(list(all_skills)):
                row = {'Skill': skill}
                for role in selected_roles:
                    row[role] = 1 if skill in role_skills_dict[role] else 0
                matrix_data.append(row)

            df_matrix = pd.DataFrame(matrix_data)

            if len(df_matrix) > 0:
                df_matrix['Total'] = df_matrix[selected_roles].sum(axis=1)
                df_matrix_sorted = df_matrix.sort_values('Total', ascending=False).head(20)

                fig_heatmap = px.imshow(
                    df_matrix_sorted[selected_roles].T,
                    labels=dict(x="Skills", y="Roles", color="Present"),
                    x=df_matrix_sorted['Skill'], y=selected_roles,
                    color_continuous_scale=[[0,'#0d1117'],[0.5,'#312e81'],[1,'#6366f1']],
                    aspect='auto'
                )
                fig_heatmap.update_layout(
                    title=dict(text="Top 20 Skills Presence Across Roles", font=dict(color='#94a3b8', size=13)),
                    height=380, xaxis_tickangle=-45,
                    margin=dict(l=10, r=10, t=40, b=10),
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)

                common_skills = df_matrix[df_matrix['Total'] == len(selected_roles)]['Skill'].tolist()
                if common_skills:
                    st.success(f"**{len(common_skills)} shared skills** across all selected roles: "
                               + ", ".join(common_skills[:10]) + ("…" if len(common_skills) > 10 else ""))

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Comparison Table")
            st.dataframe(df_comparison, use_container_width=True, height=200)
        else:
            st.warning("Please select at least 2 roles to compare.")

    # ════════════════════════════════════════════
    # PAGE: TRENDS OVER TIME
    # ════════════════════════════════════════════
    elif page == "Trends Over Time":
        st.markdown("### Trends Over Time")
        df_trends = roles_trends()
        df_trends = df_trends.sort_values("month", ascending=True)
 
        COLORS = [
            "#6366f1", "#22d3ee", "#34d399", "#f472b6",
            "#fb923c", "#a78bfa", "#38bdf8", "#facc15"
        ]
 
        fig = go.Figure()
 
        for i, role_name in enumerate(df_trends["name"].unique()):
            df_role = df_trends[df_trends["name"] == role_name]
            color = COLORS[i % len(COLORS)]
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
 
            fig.add_trace(go.Scatter(
                x=df_role["month"],
                y=df_role["jobCount"],
                name=role_name,
                mode="lines",
                line=dict(color=color, width=2.5, shape="spline", smoothing=1.2),
                fill="tozeroy",
                fillcolor=f"rgba({r},{g},{b},0.08)",
                hovertemplate=(
                    f"<b>{role_name}</b><br>"
                    "Month: %{x}<br>"
                    "Jobs: %{y:,}<extra></extra>"
                )
            ))
 
        fig.update_layout(
            height=500,
            margin=dict(l=10, r=20, t=20, b=10),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="#13172a",
                bordercolor="rgba(99,102,241,0.4)",
                font=dict(color="#e2e8f0", size=12)
            ),
            legend=dict(
                bgcolor="rgba(13,17,23,0.8)",
                bordercolor="rgba(255,255,255,0.08)",
                borderwidth=1,
                font=dict(size=12, color="#94a3b8"),
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="left", x=0
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                tickfont=dict(color="#475569", size=11),
                tickformat="%b %Y",
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.04)",
                zeroline=False,
                tickfont=dict(color="#475569", size=11),
            ),
        )
 
        st.plotly_chart(fig, use_container_width=True)
 
        with st.expander("View Raw Data"):
            st.dataframe(df_trends.sort_values("month", ascending=False), use_container_width=True)

load_dashboard()

st.markdown("---")
st.caption("Internship Job Market Intelligence  ·  Last scraped: " + f"{last_scraped_time()}")