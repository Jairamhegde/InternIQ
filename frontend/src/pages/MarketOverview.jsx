import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    AreaChart, Area, BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { Card, PageHeader, StatTile, Loader, ErrorMessage, EmptyMessage, ChartTooltip } from '../components.jsx';
import { getJson, postJson, toTitle, formatNumber, shortMonth, CHART_COLORS, AXIS_STYLE, GRID_COLOR } from '../helpers.js';
import './MarketOverview.css';

const FIELD_OPTIONS = [
    { value: 'all', label: 'All fields' },
    { value: 'backend', label: 'Backend' },
    { value: 'frontend', label: 'Frontend' },
    { value: 'mobile', label: 'Mobile' },
    { value: 'machine learning', label: 'Machine Learning' },
    { value: 'data science', label: 'Data Science' },
    { value: 'big data', label: 'Big Data' },
    { value: 'fullstack', label: 'Fullstack' },
];

const CURRENT_YEAR = new Date().getFullYear();
const YEARS = [CURRENT_YEAR - 2, CURRENT_YEAR - 1, CURRENT_YEAR];

function MarketOverview() {
    const [field, setField] = useState('all');
    const [year, setYear] = useState(CURRENT_YEAR);

    return (
        <>
            <PageHeader
                title="Market Overview"
                description="Internship hiring activity across tracked job boards."
            >
                <select className="native-select" value={field} onChange={(event) => setField(event.target.value)}>
                    {FIELD_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                </select>
            </PageHeader>

            <OverviewTiles field={field} />

            <div className="grid-wide-left">
                <JobPostingsChart field={field} year={year} setYear={setYear} />
                <TopCompanies field={field} year={year} />
            </div>

            <div className="grid-two">
                <TopSkillsTable field={field} />
                <TopRolesChart field={field} />
            </div>
        </>
    );
}

// ---------- Stat tiles: /api/job-tiles ----------

function OverviewTiles({ field }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['jobTiles', field],
        queryFn: () => getJson(`/api/job-tiles?field=${field}`),
    });

    if (isLoading) {
        return <div className="card"><Loader /></div>;
    }
    if (isError) {
        return <div className="card"><ErrorMessage /></div>;
    }

    return (
        <div className="stat-grid">
            <StatTile
                label="Opportunities tracked"
                value={data.year_posting}
                badge
                meta={`Postings in ${CURRENT_YEAR}`}
            />
            <StatTile
                label="Top role"
                value={toTitle(data.role)}
                badge
                meta={`${formatNumber(data.roleCount)} jobs`}
            />
            <StatTile
                label="Most demanded skill"
                value={toTitle(data.skill)}
                badge
                meta={`${formatNumber(data.skillCount)} mentions`}
            />
            <StatTile
                label="Top location"
                value={toTitle(data.location)}
                badge
                meta={`${formatNumber(data.locationCount)} jobs`}
            />
        </div>
    );
}

// ---------- Postings volume chart: /api/job-postings ----------

function JobPostingsChart({ field, year, setYear }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['jobPostings', year, field],
        queryFn: () => postJson('/api/job-postings', { year: year, field: field }),
    });

    const yearButtons = (
        <div className="year-buttons">
            {YEARS.map((item) => (
                <button
                    key={item}
                    className={item === year ? 'is-active' : ''}
                    onClick={() => setYear(item)}
                >
                    {item}
                </button>
            ))}
        </div>
    );

    let body;
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else if (data.length === 0) {
        body = <EmptyMessage text={`No postings recorded in ${year}.`} />;
    } else {
        const chartData = data.map((row) => ({ month: shortMonth(row.month), jobs: row.jobs }));
        body = (
            <ResponsiveContainer width="100%" height={460}>
                <AreaChart data={chartData} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
                    <defs>
                        <linearGradient id="postingsFill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor={CHART_COLORS[0]} stopOpacity={0.18} />
                            <stop offset="100%" stopColor={CHART_COLORS[0]} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid vertical={false} stroke={GRID_COLOR} />
                    <XAxis dataKey="month" {...AXIS_STYLE} dy={8} />
                    <YAxis {...AXIS_STYLE} width={48} />
                    <Tooltip content={<ChartTooltip />} />
                    <Area
                        type="monotone"
                        dataKey="jobs"
                        name="Postings"
                        stroke={CHART_COLORS[0]}
                        strokeWidth={2}
                        fill="url(#postingsFill)"
                        activeDot={{ r: 4, strokeWidth: 2, stroke: '#ffffff' }}
                    />
                </AreaChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Card title="Job postings volume" subtitle="New postings per month" action={yearButtons}>
            {body}
        </Card>
    );
}

// ---------- Top hiring companies: /api/top-companies ----------

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
        body = <EmptyMessage />;
    } else {
        body = (
            <ul className="company-list">
                {data.map((company) => (
                    <li key={company.company}>
                        <span className="company-initial">{company.company.charAt(0).toUpperCase()}</span>
                        <span className="company-name" title={toTitle(company.company)}>
                            {toTitle(company.company)}
                        </span>
                        <span className="company-count">{formatNumber(company.count)} jobs</span>
                    </li>
                ))}
            </ul>
        );
    }

    return (
        <Card title="Top hiring companies" subtitle={`Postings in ${year}`}>
            {body}
        </Card>
    );
}

// ---------- Top skills table: /api/top-skills ----------

function TopSkillsTable({ field }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['topSkills', field],
        queryFn: () => getJson(`/api/top-skills?field=${field}`),
    });

    let body;
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else {
        body = (
            <div className="table-wrap">
                <table className="table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Skill</th>
                            <th className="cell-number">Mentions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((row, index) => (
                            <tr key={row.name}>
                                <td className="rank-cell">{index + 1}</td>
                                <td className="cell-strong">{toTitle(row.name)}</td>
                                <td className="cell-number">{formatNumber(row.demand)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    }

    return (
        <Card title="Top in-demand skills" subtitle="Top 5 skills by number of postings">
            {body}
        </Card>
    );
}

// ---------- Top roles chart: /api/top-role-table ----------

function TopRolesChart({ field }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['topRoles', field, 5],
        queryFn: () => getJson(`/api/top-role-table?field=${field}&limit=5`),
    });

    let body;
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else {
        body = (
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data} layout="vertical" margin={{ top: 0, right: 40, left: 0, bottom: 0 }}>
                    <CartesianGrid horizontal={false} stroke={GRID_COLOR} />
                    <XAxis type="number" {...AXIS_STYLE} />
                    <YAxis
                        type="category"
                        dataKey="role"
                        width={170}
                        tickFormatter={toTitle}
                        {...AXIS_STYLE}
                    />
                    <Tooltip content={<ChartTooltip labelFormatter={toTitle} />} cursor={{ fill: '#f3f3f0' }} />
                    <Bar
                        dataKey="volume"
                        name="Postings"
                        fill={CHART_COLORS[0]}
                        radius={[0, 4, 4, 0]}
                        maxBarSize={22}
                        label={{ position: 'right', fill: '#57564f', fontSize: 12 }}
                    />
                </BarChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Card title="Top roles" subtitle="Top 5 roles by number of postings">
            {body}
        </Card>
    );
}

export default MarketOverview;
