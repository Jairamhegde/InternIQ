
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    AreaChart, Area, BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import {
    PageLayout, Panel, Stat, ChipGroup, Loader, ErrorMessage, EmptyMessage, ChartTooltip, SourceTag,
} from '../components.jsx';
import {
    getJson, postJson, toTitle, formatNumber, shortMonth, daysAgo,
    CHART_COLORS, AXIS_STYLE, LABEL_COLOR, LABEL_TICK, GRID_COLOR, HOVER_CURSOR, ACTIVE_DOT_RING,
} from '../helpers.js';

const CURRENT_YEAR = new Date().getFullYear();

// colour for the job postings chart
const POSTINGS_CHART_COLOR = '#2dd4bf';

const FIELD_OPTIONS = [
    { value: 'all', label: 'All fields' },
    { value: 'backend', label: 'Backend' },
    { value: 'frontend', label: 'Frontend' },
    { value: 'fullstack', label: 'Full stack' },
    { value: 'mobile', label: 'Mobile' },
    { value: 'machine learning', label: 'Machine learning' },
    { value: 'data science', label: 'Data science' },
    { value: 'big data', label: 'Big data' },
];

const YEAR_OPTIONS = [
    { value: CURRENT_YEAR, label: String(CURRENT_YEAR) },
    { value: CURRENT_YEAR - 1, label: String(CURRENT_YEAR - 1) },
];

const SUGGESTED_QUESTIONS = [
    'Which role has the most postings?',
    'Which skill should I learn first?',
    'Where are most jobs located?',
];

function MarketOverview({ onOpen, onAsk }) {
    const [field, setField] = useState('all');
    const [year, setYear] = useState(CURRENT_YEAR);

    const tilesQuery = useQuery({
        queryKey: ['jobTiles', field],
        queryFn: () => getJson(`/api/job-tiles?field=${field}`),
    });

    let basedOn = null;
    if (tilesQuery.data) {
        basedOn = <span className="based-on">Based on {tilesQuery.data.year_posting} postings in {CURRENT_YEAR}</span>;
    }

    const sidebar = (
        <>
            <ChipGroup label="Field" options={FIELD_OPTIONS} value={field} onChange={setField} />
            <ChipGroup label="Year" options={YEAR_OPTIONS} value={year} onChange={setYear} />
            <div className="filter-group">
                <span className="filter-label">Sources</span>
                <p className="filter-hint">Internshala, Greenhouse and Ashby job boards, collected every day.</p>
            </div>
        </>
    );

    return (
        <PageLayout

            aside={basedOn}
            sidebar={sidebar}
            sidebarTitle="Filters"
        >
            <AskBox onAsk={onAsk} />

            <OverviewStats query={tilesQuery} field={field} />

            <div className="row row-wide">
                <PostingsChart field={field} year={year} />
                <RecentlyScanned onOpen={onOpen} />
            </div>

            <div className="row">
                <TopRoles field={field} />
                <TopSkills field={field} />
            </div>

            <TopCompanies field={field} year={year} />
        </PageLayout>
    );
}

// ask the market box

function AskBox({ onAsk }) {
    const [question, setQuestion] = useState('');

    function handleSubmit(event) {
        event.preventDefault();
        const cleanQuestion = question.trim();
        if (cleanQuestion !== '') {
            onAsk(cleanQuestion);
        }
    }

    return (
        <Panel title="Ask the market" className="ask-box">
            <form className="ask-form" onSubmit={handleSubmit}>
                <label htmlFor="ask-market" className="sr-only">Your question</label>
                <input
                    id="ask-market"
                    placeholder="For example, which skill gets me hired fastest?"
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                />
                <button className="btn btn-primary" type="submit" disabled={question.trim() === ''}>
                    Ask
                </button>
            </form>
            <div className="suggestions">
                {SUGGESTED_QUESTIONS.map((suggestion) => (
                    <button key={suggestion} className="suggestion" onClick={() => onAsk(suggestion)}>
                        {suggestion}
                    </button>
                ))}
            </div>
        </Panel>
    );
}

// overview stats

function OverviewStats({ query, field }) {
    if (query.isLoading) {
        return <Panel><Loader /></Panel>;
    }
    if (query.isError) {
        return <Panel><ErrorMessage /></Panel>;
    }

    const data = query.data;
    const fieldLabel = FIELD_OPTIONS.find((option) => option.value === field).label;

    return (
        <div className="stats">
            <Stat label={`Postings in ${CURRENT_YEAR}`} value={data.year_posting} meta={fieldLabel} />
            <Stat label="Most posted role" value={toTitle(data.role)} meta={`${formatNumber(data.roleCount)} postings`} />
            <Stat label="Most asked skill" value={toTitle(data.skill)} meta={`In ${formatNumber(data.skillCount)} postings`} />
            <Stat label="Most common location" value={toTitle(data.location)} meta={`${formatNumber(data.locationCount)} postings`} />
        </div>
    );
}

// job postings per month chart

function PostingsChart({ field, year }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['jobPostings', year, field],
        queryFn: () => postJson('/api/job-postings', { year: year, field: field }),
    });

    let body;
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else if (data.length === 0) {
        body = <EmptyMessage title={`No postings for ${year}`} text="No postings were collected in this year. Pick another year in the filters." />;
    } else {
        const chartData = data.map((row) => ({ month: shortMonth(row.month), jobs: row.jobs }));

        let note = null;
        if (year === CURRENT_YEAR) {
            note = <p className="chart-note">The current month is still in progress, so its count is still growing.</p>;
        }

        body = (
            <>
                <ResponsiveContainer width="100%" height={420}>
                    <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="postingsFill" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor={POSTINGS_CHART_COLOR} stopOpacity={0.45} />
                                <stop offset="100%" stopColor={POSTINGS_CHART_COLOR} stopOpacity={0.02} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid vertical={false} stroke={GRID_COLOR} />
                        <XAxis dataKey="month" {...AXIS_STYLE} dy={8} />
                        <YAxis {...AXIS_STYLE} width={52} tickFormatter={formatNumber} />
                        <Tooltip content={<ChartTooltip />} cursor={{ stroke: GRID_COLOR }} />
                        <Area
                            isAnimationActive={false}
                            type="monotone"
                            dataKey="jobs"
                            name="Postings"
                            stroke={POSTINGS_CHART_COLOR}
                            strokeWidth={2.5}
                            fill="url(#postingsFill)"
                            activeDot={{ r: 4, strokeWidth: 2, stroke: ACTIVE_DOT_RING }}
                        />
                    </AreaChart>
                </ResponsiveContainer>
                {note}
            </>
        );
    }

    return (
        <Panel title="Job postings per month" subtitle={`New postings in ${year}`}>
            {body}
        </Panel>
    );
}

// recently scanned jobs

function RecentlyScanned({ onOpen }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['recentPostings'],
        queryFn: () => getJson('/api/job-posting-list'),
    });

    let body;
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else if (data.length === 0) {
        body = <EmptyMessage title="No postings in the last 10 days" />;
    } else {
        const newestJobs = data.slice(0, 5);
        body = (
            <ul className="job-list">
                {newestJobs.map((job, index) => (
                    <li key={index}>
                        <a href={job.job_link} target="_blank" rel="noreferrer" className="job-title">{toTitle(job.title)}</a>
                        <span className="job-company">{toTitle(job.company)}</span>
                        <span className="job-tags">
                            <SourceTag />
                            <span className="tag tag-quiet">{daysAgo(job.posted_date)}</span>
                        </span>
                    </li>
                ))}
            </ul>
        );
    }

    const seeAllButton = (
        <button className="link-button" onClick={() => onOpen('trends')}>See all</button>
    );

    return (
        <Panel title="Recently scanned jobs" action={seeAllButton}>
            {body}
        </Panel>
    );
}

// top roles chart

function TopRoles({ field }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['topRoles', field, 5],
        queryFn: () => getJson(`/api/top-role-table?field=${field}&limit=5`),
    });

    let body;
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else if (data.length === 0) {
        body = <EmptyMessage title="No roles found" />;
    } else {
        body = (
            <ResponsiveContainer width="100%" height={260}>
                <BarChart data={data} layout="vertical" margin={{ top: 0, right: 44, left: 0, bottom: 0 }}>
                    <CartesianGrid horizontal={false} stroke={GRID_COLOR} />
                    <XAxis type="number" {...AXIS_STYLE} />
                    <YAxis type="category" dataKey="role" width={160} tickFormatter={toTitle} {...AXIS_STYLE} tick={LABEL_TICK} />
                    <Tooltip content={<ChartTooltip labelFormatter={toTitle} />} cursor={HOVER_CURSOR} />
                    <Bar
                        isAnimationActive={false}
                        dataKey="volume"
                        name="Postings"
                        fill={CHART_COLORS[0]}
                        radius={[0, 4, 4, 0]}
                        maxBarSize={20}
                        label={{ position: 'right', fill: LABEL_COLOR, fontSize: 12 }}
                    />
                </BarChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Panel title="Top roles" subtitle="Roles with the most postings">
            {body}
        </Panel>
    );
}

// top skills table

function TopSkills({ field }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['topSkills', field],
        queryFn: () => getJson(`/api/top-skills?field=${field}`),
    });

    let body;
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else if (data.length === 0) {
        body = <EmptyMessage title="No skills found" />;
    } else {
        const highestDemand = data[0].demand;
        body = (
            <table className="table">
                <thead>
                    <tr>
                        <th className="col-rank">Rank</th>
                        <th>Skill</th>
                        <th className="col-num">Postings</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, index) => {
                        const barWidth = (row.demand / highestDemand) * 100;
                        return (
                            <tr key={row.name}>
                                <td className="col-rank">{index + 1}</td>
                                <td className="cell-strong">
                                    {toTitle(row.name)}
                                    <span className="cell-bar"><i style={{ width: `${barWidth}%` }} /></span>
                                </td>
                                <td className="col-num">{formatNumber(row.demand)}</td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        );
    }

    return (
        <Panel title="Most asked skills" subtitle="Skills mentioned in the most postings">
            {body}
        </Panel>
    );
}

// top hiring companies

function TopCompanies({ field, year }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['topCompanies', year, field],
        queryFn: () => postJson('/api/top-companies', { year: year, field: field }),
    });

    let body;
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else if (data.length === 0) {
        body = <EmptyMessage title={`No hiring data for ${year}`} text="Pick another year in the filters." />;
    } else {
        const topEight = data.slice(0, 8);
        body = (
            <ol className="company-grid">
                {topEight.map((company) => (
                    <li key={company.company}>
                        <span className="company-initial" aria-hidden="true">{company.company.charAt(0).toUpperCase()}</span>
                        <span className="company-name" title={toTitle(company.company)}>{toTitle(company.company)}</span>
                        <span className="company-count">{formatNumber(company.count)}</span>
                    </li>
                ))}
            </ol>
        );
    }

    return (
        <Panel title="Top hiring companies" subtitle={`Postings in ${year}`}>
            {body}
        </Panel>
    );
}

export default MarketOverview;
