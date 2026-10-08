import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { Card, PageHeader, StatTile, Icon, Loader, ErrorMessage, EmptyMessage, ChartTooltip } from '../components.jsx';
import { getJson, toTitle, formatNumber, formatRupee, CHART_COLORS, BLUE_RAMP, AXIS_STYLE, GRID_COLOR } from '../helpers.js';
import './RecentMarketTrend.css';

function RecentMarketTrend() {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['recentMarketTrend'],
        queryFn: () => getJson('/api/recent-market-trend'),
    });

    return (
        <>
            <PageHeader title="Recent Market Trends" description="Market activity over the last 10 days." />

            {isLoading && <div className="card"><Loader /></div>}
            {isError && <div className="card"><ErrorMessage /></div>}
            {data && <TrendTiles trend={data} />}

            <div className="grid-wide-left">
                <RolePostingsChart trend={data} isLoading={isLoading} isError={isError} />
                <TopLocationsChart />
            </div>

            <RecentPostingsTable />
        </>
    );
}

// ---------- Stat tiles: /api/recent-market-trend ----------
// role, skill and toplocation arrive as [name, count] pairs.

function TrendTiles({ trend }) {
    const [roleName, roleCount] = trend.role;
    const [skillName, skillCount] = trend.skill;
    const [locationName, locationCount] = trend.toplocation;

    let stipend = 'N/A';
    if (trend.average_sal) {
        stipend = formatRupee(trend.average_sal);
    }

    return (
        <div className="stat-grid trend-stat-grid">
            <StatTile
                label="Total opportunities"
                value={formatNumber(trend.postings)}
                change={trend.increment}
                meta="vs previous period"
            />
            <StatTile badge label="Most demanded skill" value={toTitle(skillName)} meta={`${formatNumber(skillCount)} mentions`} />
            <StatTile badge label="Most demanded role" value={toTitle(roleName)} meta={`${formatNumber(roleCount)} jobs`} />
            <StatTile label="Top role avg stipend" value={stipend} meta={toTitle(roleName)} />
            <StatTile badge label="Top location" value={toTitle(locationName)} meta={`${formatNumber(locationCount)} jobs`} />
        </div>
    );
}

// ---------- Postings by role: toproles from /api/recent-market-trend ----------

function RolePostingsChart({ trend, isLoading, isError }) {
    let body;
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else if (trend.toproles.length === 0) {
        body = <EmptyMessage />;
    } else {
        body = (
            <ResponsiveContainer width="100%" height={320}>
                <BarChart data={trend.toproles} margin={{ top: 20, right: 8, left: 40, bottom: 0 }} barCategoryGap="30%">
                    <CartesianGrid vertical={false} stroke={GRID_COLOR} />
                    <XAxis
                        dataKey="role"
                        tickFormatter={toTitle}
                        interval={0}
                        angle={-25}
                        textAnchor="end"
                        height={90}
                        {...AXIS_STYLE}
                    />
                    <YAxis {...AXIS_STYLE} width={48} />
                    <Tooltip content={<ChartTooltip labelFormatter={toTitle} />} cursor={{ fill: '#f3f3f0' }} />
                    <Bar
                        dataKey="volume"
                        name="Postings"
                        fill={CHART_COLORS[0]}
                        radius={[4, 4, 0, 0]}
                        maxBarSize={44}
                        label={{ position: 'top', fill: '#57564f', fontSize: 12 }}
                    />
                </BarChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Card title="Job postings by role" subtitle="Last 10 days">
            {body}
        </Card>
    );
}

// ---------- Top locations pie chart: /api/get-top-locations ----------

function TopLocationsChart() {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['topLocations'],
        queryFn: () => getJson('/api/get-top-locations'),
    });

    let body;
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else if (data.length === 0) {
        body = <EmptyMessage />;
    } else {
        // The API also sends bright "fill" colours; this chart uses its own muted ones instead.
        const chartData = data.map((row) => ({ name: toTitle(row.name), value: row.value }));
        let total = 0;
        for (const row of chartData) {
            total = total + row.value;
        }

        body = (
            <>
                <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                        <Pie
                            data={chartData}
                            dataKey="value"
                            nameKey="name"
                            innerRadius={55}
                            outerRadius={88}
                            paddingAngle={2}
                            stroke="#ffffff"
                            strokeWidth={2}
                        >
                            {chartData.map((row, index) => (
                                <Cell key={row.name} fill={BLUE_RAMP[index % BLUE_RAMP.length]} />
                            ))}
                        </Pie>
                        <Tooltip content={<ChartTooltip />} />
                    </PieChart>
                </ResponsiveContainer>

                <ul className="location-legend">
                    {chartData.map((row, index) => (
                        <li key={row.name}>
                            <span className="swatch" style={{ background: BLUE_RAMP[index % BLUE_RAMP.length] }} />
                            <span className="location-name">{row.name}</span>
                            <span className="location-value">{formatNumber(row.value)}</span>
                            <span className="location-share">{Math.round((row.value / total) * 100)}%</span>
                        </li>
                    ))}
                </ul>
            </>
        );
    }

    return (
        <Card title="Top locations" subtitle="Last 10 days">
            {body}
        </Card>
    );
}

// ---------- Recent postings table: /api/job-posting-list ----------

function RecentPostingsTable() {
    const [search, setSearch] = useState('');

    const { data, isLoading, isError } = useQuery({
        queryKey: ['recentPostings'],
        queryFn: () => getJson('/api/job-posting-list'),
    });

    const searchBox = (
        <input
            className="table-search"
            type="search"
            placeholder="Search role or company"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
        />
    );

    let body;
    let subtitle = '';
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else {
        const searchText = search.trim().toLowerCase();
        const rows = data.filter((row) => {
            const title = String(row.title).toLowerCase();
            const company = String(row.company).toLowerCase();
            return title.includes(searchText) || company.includes(searchText);
        });
        subtitle = `${rows.length} of ${data.length} postings`;

        body = (
            <div className="table-wrap postings-scroll">
                <table className="table">
                    <thead>
                        <tr>
                            <th>Role</th>
                            <th>Company</th>
                            <th>Posted date</th>
                            <th className="cell-number">Link</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((row, index) => (
                            <tr key={index}>
                                <td className="cell-strong">{toTitle(row.title)}</td>
                                <td>{toTitle(row.company)}</td>
                                <td className="posted-date">{formatDate(row.posted_date)}</td>
                                <td className="cell-number">
                                    {row.job_link ? (
                                        <a className="posting-link" href={row.job_link} target="_blank" rel="noreferrer">
                                            View <Icon name="external" size={13} />
                                        </a>
                                    ) : (
                                        <span className="posted-date">Unavailable</span>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {rows.length === 0 && <EmptyMessage text="No postings match your search." />}
            </div>
        );
    }

    return (
        <Card title="Recent job postings" subtitle={subtitle} action={searchBox}>
            {body}
        </Card>
    );
}

// "2026-10-04" -> "04 Oct"
function formatDate(isoDate) {
    const date = new Date(isoDate);
    return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
}

export default RecentMarketTrend;
