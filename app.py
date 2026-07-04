import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import streamlit as st

from queries.analysis import (
    roles, noOfopportunities, roles_trends,
    TopSkillsOfRole, jobCount, topSkills,
    topLocations, commonSkills, last_scraped_time
)
from queries.recent_market_trends import Top_role, top_skill, total_opportunities, average_salary

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

from utils.html_templates import (
    STYLES, BRAND_HEADER_HTML, COMPARE_DIVIDER_HTML, PAGE_SUBTITLE_HTML,
    CROSS_FUNCTIONAL_SUBTEXT_HTML, MOST_IN_DEMAND_SKILLS_HEADER,
    SKILL_PRIORITY_SUBTEXT_HTML, MUST_HAVE_SKILLS_HEADER_HTML,
    EMERGING_SKILLS_HEADER_HTML, CLOSE_DIV_HTML, BR_HTML,
    insight_card, key_insight_card, insights_section,
    get_market_analysis_html, get_skill_market_analysis_html
)

NAV_ICONS = {
    "Overall Market Trends":  "",
    "Recent Market Trend":    "",
    "Role-Specific Analysis": "",
    "Comparative Analysis":   "",
    "Trends Over Time":       "",
}


def load_dashboard():
    st.markdown(STYLES, unsafe_allow_html=True)

    @st.cache_data(ttl=3600)
    def load_all_data():
        return {
            'roles':        roles(),
            'skills':       topSkills(),
            'locations':    topLocations(),
            'common_roles': commonSkills(),
            'opportunity':  noOfopportunities()
        }

    data = load_all_data()
    df_roles                = data['roles']
    df_skills               = data['skills']
    df_locations            = data['locations']
    cross_functional_skills = data['common_roles']

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        # Brand header
        st.markdown(BRAND_HEADER_HTML, unsafe_allow_html=True)

        pages = [
            "Overall Market Trends",
            "Recent Market Trend",
            "Role-Specific Analysis",
        ]
        compare_pages = [
            "Comparative Analysis",
            "Trends Over Time",
        ]

        if "page" not in st.session_state:
            st.session_state.page = pages[0]

        for pg in pages:
            label = f"{pg}"
            if st.button(label, key=f"nav_{pg}", use_container_width=True):
                st.session_state.page = pg

        # Divider + second section label
        st.markdown(COMPARE_DIVIDER_HTML, unsafe_allow_html=True)

        for pg in compare_pages:
            
            label = f"{pg}"
            if st.button(label, key=f"nav_{pg}", use_container_width=True):
                st.session_state.page = pg

        page = st.session_state.page
        total_job_count = data['opportunity']

    # ── PAGE HEADER ───────────────────────────────────────────────────────────
    st.markdown("# Internship Job Market Intelligence")
    st.markdown(PAGE_SUBTITLE_HTML, unsafe_allow_html=True)

    # ── PAGE: OVERALL MARKET TRENDS ──────────────────────────────────────────
    if page == "Overall Market Trends":
        st.markdown("### Market Overview")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Opportunities Tracked", f"{total_job_count:,}", "Active Postings")
        with col2:
            top_role = df_roles.iloc[0]['title'].capitalize()
            st.metric("Top Role",
                      top_role[:20] + "…" if len(str(top_role)) > 20 else top_role,
                      f"{df_roles.iloc[0]['demand']} jobs")
        with col3:
            st.metric("Most Demanded Skill", df_skills.iloc[0]['name'].capitalize(),
                      f"{df_skills.iloc[0]['demand']} mentions")
        with col4:
            st.metric("Top Location", df_locations.iloc[0]['location'].capitalize(),
                      f"{df_locations.iloc[0]['count']} jobs")

        st.markdown(BR_HTML, unsafe_allow_html=True)
        st.markdown("### Market Demand Analysis")
        st.markdown(BR_HTML, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top 10 In-Demand Roles**")
            fig_roles = px.bar(
                df_roles, x='demand', y='title', orientation='h', text='demand',
                labels={'demand': 'Job Postings', 'id': ''}
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

        st.markdown(BR_HTML, unsafe_allow_html=True)
        st.markdown("### Geographic Distribution")

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
                df_roles.head(8), values='demand', names='title', hole=0.55,
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
            st.markdown(BR_HTML, unsafe_allow_html=True)
            st.markdown("### Cross-Functional Skills")
            st.markdown(CROSS_FUNCTIONAL_SUBTEXT_HTML, unsafe_allow_html=True)
            fig_common = px.bar(
                cross_functional_skills.head(15), x='total_occurrences', y='skill',
                orientation='h', text='total_occurrences',
                labels={'total_occurrences': 'Total Occurrences', 'skill': ''}
            )
            fig_common.update_traces(
                texttemplate='%{text}', textposition='outside',
                textfont=dict(color='#94a3b8', size=11),
                marker=dict(color=cross_functional_skills['role_count'],
                            colorscale=[[0,'#1e1b4b'],[1,'#a78bfa']])
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

    # ── PAGE: RECENT MARKET TREND ─────────────────────────────────────────────
    elif page == "Recent Market Trend":
        toprole           = Top_role()
        topSkill_df       = top_skill()
        total_opportunity = total_opportunities()
        salary_range      = average_salary(toprole.iloc[0]['title'])

        st.markdown("### Last 10 Days Market Trends")
        st.markdown(BR_HTML, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Opportunities", total_opportunity['total_opportunities'][0], "Active postings")
        with col2:
            st.metric("Demanding Skill", topSkill_df['skill'][0].capitalize(), f"{topSkill_df['skill_count'][0]} mentions")
        with col3:
            st.metric("Demanding Role", toprole['title'][0].capitalize(), f"{toprole['job_count'][0]} posted")
        with col4:
            st.metric("Salary range", f"₹{int(salary_range.iloc[0]['minimum'])//12}-₹{int(salary_range.iloc[0]['maximum'])//12}", "Per month")

        chart = px.bar(
            toprole, x="title", y="job_count",
            text='job_count',
            labels={"job_count": "Number of jobs", "title": "Job title"},
            color='job_count',
            color_continuous_scale=[[0,'#1e1b4b'],[1,'#6366f1']]
        )
        chart.update_traces(textposition='outside')
        st.plotly_chart(chart, use_container_width=True)

        st.markdown(get_market_analysis_html(toprole), unsafe_allow_html=True)

        st.markdown(BR_HTML, unsafe_allow_html=True)
        st.markdown(MOST_IN_DEMAND_SKILLS_HEADER, unsafe_allow_html=True)
        st.markdown(BR_HTML, unsafe_allow_html=True)

        skill_chart = px.bar(
            topSkill_df, x="skill", y="skill_count",
            labels={"skill": "Skill", "skill_count": "Mentions"},
            color="skill_count",
            color_continuous_scale=[[0,"#0f2a10"],[1,"#52c558"]]
        )
        st.plotly_chart(skill_chart, use_container_width=True)

        st.markdown(get_skill_market_analysis_html(topSkill_df), unsafe_allow_html=True)

        st.markdown(BR_HTML, unsafe_allow_html=True)

    # ── PAGE: ROLE-SPECIFIC ANALYSIS ──────────────────────────────────────────
    elif page == "Role-Specific Analysis":
        st.markdown("### Role-Specific Analysis")

        col1, col2 = st.columns([2, 1])
        with col1:
            selected_role = st.selectbox("Select a role:", df_roles['title'].tolist(), key="role_selector")
        with col2:
            role_rank = df_roles[df_roles['title'] == selected_role].index[0] + 1
            st.metric("Role Ranking", f"#{role_rank}", f"out of {len(df_roles)}")

        salaries       = average_salary(selected_role)
        df_role_skills = TopSkillsOfRole(selected_role)
        df_job_count   = jobCount(selected_role)
        total_jobs     = df_job_count.iloc[0]['no_of_jobs']

        st.markdown(BR_HTML, unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Openings", f"{total_jobs}", "Active Positions")
        with col2:
            st.metric("Required Skills", f"{len(df_role_skills)}", "Unique skills")
        with col3:
            avg_skills = df_role_skills['demand'].mean()
            st.metric("Avg. Skill Mentions", f"{avg_skills:.0f}", "per skill")
        with col4:
            st.metric("AVG Salary", f"₹{int(salaries.iloc[0]['average'])//12 if salaries.iloc[0]['average'] else "NA"}", "Per month")

        st.markdown(BR_HTML, unsafe_allow_html=True)
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
                st.markdown(SKILL_PRIORITY_SUBTEXT_HTML, unsafe_allow_html=True)
                top_skill_pct = (df_role_skills.iloc[0]['demand'] / df_role_skills['demand'].sum()) * 100
                st.progress(top_skill_pct / 100)
                st.caption(f"**{df_role_skills.iloc[0]['name']}** in {top_skill_pct:.1f}% of requirements")

        st.markdown(BR_HTML, unsafe_allow_html=True)
        st.markdown("### Career Insights")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(MUST_HAVE_SKILLS_HEADER_HTML, unsafe_allow_html=True)
            for idx, row in df_role_skills.head(3).iterrows():
                pct = (row['demand'] / total_jobs) * 100
                st.markdown(f"**{idx+1}. {row['name']}** — Required in {pct:.0f}% of postings")
            st.markdown(CLOSE_DIV_HTML, unsafe_allow_html=True)

        with col2:
            st.markdown(EMERGING_SKILLS_HEADER_HTML, unsafe_allow_html=True)
            if len(df_role_skills) > 5:
                for _, row in df_role_skills.tail(3).iterrows():
                    st.markdown(f"• **{row['name']}** — {row['demand']} mentions")
            else:
                st.info("Not enough data for emerging skills analysis")
            st.markdown(CLOSE_DIV_HTML, unsafe_allow_html=True)

        with st.expander("View Complete Skills Data"):
            st.dataframe(df_role_skills, use_container_width=True, height=380)

    # ── PAGE: COMPARATIVE ANALYSIS ────────────────────────────────────────────
    elif page == "Comparative Analysis":
        import numpy as np

        st.markdown("### Comparative Role Analysis")
        st.markdown(
            "<p style='color:#64748b;font-size:13px;margin-top:-6px'>Compare roles side by side</p>",
            unsafe_allow_html=True
        )

        selected_roles = st.multiselect(
            "Select 2–4 roles to compare:",
            df_roles['title'].tolist(),
            default=df_roles['title'].tolist()[:3],
            max_selections=4
        )

        if len(selected_roles) >= 2:
            comparison_data = []
            for role in selected_roles:
                jc     = jobCount(role).iloc[0]['no_of_jobs']
                skills = TopSkillsOfRole(role)
                comparison_data.append({
                    'Role':             role,
                    'Jobs':             jc,
                    'Unique Skills':    len(skills),
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

            st.markdown(BR_HTML, unsafe_allow_html=True)
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
                df_matrix_sorted   = df_matrix.sort_values('Total', ascending=False).head(20)

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

                common = df_matrix[df_matrix['Total'] == len(selected_roles)]['Skill'].tolist()
                if common:
                    st.success(
                        f"**{len(common)} shared skills** across all selected roles: "
                        + ", ".join(common[:10])
                        + ("…" if len(common) > 10 else "")
                    )

            st.markdown(BR_HTML, unsafe_allow_html=True)
            st.markdown("### Comparison Table")
            st.dataframe(df_comparison, use_container_width=True, height=200)
        else:
            st.warning("Please select at least 2 roles to compare.")

    # ── PAGE: TRENDS OVER TIME ────────────────────────────────────────────────
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
            color   = COLORS[i % len(COLORS)]
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

            fig.add_trace(go.Scatter(
                x=df_role["month"],
                y=df_role["jobcount"],
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
                xanchor="left",   x=0
            ),
            xaxis=dict(showgrid=False, zeroline=False,
                       tickfont=dict(color="#475569", size=11)),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                       zeroline=False, tickfont=dict(color="#475569", size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("View Raw Data"):
            st.dataframe(df_trends.sort_values("month", ascending=False), use_container_width=True)


load_dashboard()

st.markdown("---")
st.caption("Internship Job Market Intelligence  ·  Last scraped: " + f"{last_scraped_time()}")