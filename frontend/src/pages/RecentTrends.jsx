import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import {
    PageLayout, Panel, Stat, Loader, ErrorMessage, EmptyMessage, ChartTooltip, SourceTag,
} from '../components.jsx';
import {
    getJson, toTitle, formatNumber, formatRupee, formatDay,
    CHART_COLORS, BLUE_RAMP, AXIS_STYLE, LABEL_COLOR, GRID_COLOR, HOVER_CURSOR,
} from '../helpers.js';

function RecentTrends() {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['recentMarketTrend'],
        queryFn: () => getJson('/api/recent-market-trend'),
    });

    let stats;
    if (isLoading) {
        stats = <Panel><Loader /></Panel>;
    } else if (isError) {
        stats = <Panel><ErrorMessage /></Panel>;
    } else {
        stats = <TrendStats trend={data} />;
    }

    return (
        <PageLayout
            title="Last 10 days"
            description="The newest postings and what changed since the 10 days before."
        >
            {stats}

            <div className="row row-wide">
                <RolePostingsChart trend={data} isLoading={isLoading} isError={isError} />
                <TopLocationsChart />
            </div>

            <RecentPostingsTable />
        </PageLayout>
    );
}

// last 10 days stats

function TrendStats({ trend }) {
    const roleName = trend.role[0];
    const roleCount = trend.role[1];
    const skillName = trend.skill[0];
    const skillCount = trend.skill[1];

    let changeText = `Up ${Math.abs(trend.increment).toFixed(1)}% on the 10 days before`;
    let changeTone = 'good';
    if (trend.increment < 0) {
        changeText = `Down ${Math.abs(trend.increment).toFixed(1)}% on the 10 days before`;
        changeTone = 'bad';
    }

    let salary = 'Not available';
    if (trend.average_sal) {
        salary = formatRupee(trend.average_sal);
    }

    return (
        <div className="stats">
            <Stat label="New postings" value={formatNumber(trend.postings)} meta={changeText} tone={changeTone} />
            <Stat label="Most posted role" value={toTitle(roleName)} meta={`${formatNumber(roleCount)} postings`} />
            <Stat label="Most asked skill" value={toTitle(skillName)} meta={`${formatNumber(skillCount)} mentions`} />
            <Stat label="Average salary, top role" value={salary} meta="From postings that list a salary" />
        </div>
    );
}

// postings by role chart

function RolePostingsChart({ trend, isLoading, isError }) {
    let body;
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else if (trend.toproles.length === 0) {
        body = <EmptyMessage title="No postings in the last 10 days" />;
    } else {
        body = (
            <ResponsiveContainer width="100%" height={280}>
                <BarChart data={trend.toproles} margin={{ top: 22, right: 8, left: 24, bottom: 0 }} barCategoryGap="30%">
                    <CartesianGrid vertical={false} stroke={GRID_COLOR} />
                    <XAxis
                        dataKey="role"
                        tickFormatter={toTitle}
                        interval={0}
                        angle={-18}
                        textAnchor="end"
                        height={70}
                        {...AXIS_STYLE}
                    />
                    <YAxis {...AXIS_STYLE} width={40} allowDecimals={false} />
                    <Tooltip content={<ChartTooltip labelFormatter={toTitle} />} cursor={HOVER_CURSOR} />
                    <Bar
                        isAnimationActive={false}
                        dataKey="volume"
                        name="Postings"
                        fill={CHART_COLORS[0]}
                        radius={[4, 4, 0, 0]}
                        maxBarSize={44}
                        label={{ position: 'top', fill: LABEL_COLOR, fontSize: 12 }}
                    />
                </BarChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Panel title="Postings by role" subtitle="Last 10 days">
            {body}
        </Panel>
    );
}

// top locations chart

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
        body = <EmptyMessage title="No locations recorded" />;
    } else {
        // use our own colours instead of the api colours
        const chartData = data.map((row) => ({ name: toTitle(row.name), value: row.value }));

        let total = 0;
        for (const row of chartData) {
            total = total + row.value;
        }

        body = (
            <div className="donut">
                <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                        <Pie
                            isAnimationActive={false}
                            data={chartData}
                            dataKey="value"
                            nameKey="name"
                            innerRadius={52}
                            outerRadius={80}
                            paddingAngle={2}
                            stroke="none"
                        >
                            {chartData.map((row, index) => (
                                <Cell key={row.name} fill={BLUE_RAMP[index % BLUE_RAMP.length]} />
                            ))}
                        </Pie>
                        <Tooltip content={<ChartTooltip />} />
                    </PieChart>
                </ResponsiveContainer>
                <ul className="legend">
                    {chartData.map((row, index) => (
                        <li key={row.name}>
                            <span className="dot" style={{ background: BLUE_RAMP[index % BLUE_RAMP.length] }} />
                            <span className="legend-name">{row.name}</span>
                            <span className="legend-value">{formatNumber(row.value)}</span>
                            <span className="legend-share">{Math.round((row.value / total) * 100)}%</span>
                        </li>
                    ))}
                </ul>
            </div>
        );
    }

    return (
        <Panel title="Top locations" subtitle="Last 10 days">
            {body}
        </Panel>
    );
}

// recent postings table

function RecentPostingsTable() {
    const [search, setSearch] = useState('');

    const { data, isLoading, isError } = useQuery({
        queryKey: ['recentPostings'],
        queryFn: () => getJson('/api/job-posting-list'),
    });

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

        subtitle = `${data.length} postings`;
        if (searchText !== '') {
            subtitle = `${rows.length} of ${data.length} postings match "${search.trim()}"`;
        }

        if (rows.length === 0) {
            body = <EmptyMessage title={`No postings match "${search.trim()}"`} text="Try a shorter word, like a role or a company name." />;
        } else {
            body = (
                <div className="table-scroll">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Role</th>
                                <th>Company</th>
                                <th>Posted</th>
                                <th>Source</th>
                                <th className="col-num"><span className="sr-only">Link</span></th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((row, index) => (
                                <tr key={index}>
                                    <td className="cell-strong">{toTitle(row.title)}</td>
                                    <td className="cell-muted">{toTitle(row.company)}</td>
                                    <td className="cell-muted">{formatDay(row.posted_date)}</td>
                                    <td><SourceTag /></td>
                                    <td className="col-num"><PostingLink link={row.job_link} /></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            );
        }
    }

    const searchBox = (
        <>
            <label htmlFor="posting-search" className="sr-only">Search postings</label>
            <input
                id="posting-search"
                className="input table-search"
                type="search"
                placeholder="Search role or company"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
            />
        </>
    );

    return (
        <Panel title="Recent postings" subtitle={subtitle} action={searchBox}>
            {body}
        </Panel>
    );
}

function PostingLink({ link }) {
    if (!link) {
        return <span className="cell-muted">No link</span>;
    }
    return <a className="link" href={link} target="_blank" rel="noreferrer">Open posting</a>;
}

export default RecentTrends;
