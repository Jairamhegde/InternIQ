import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    BarChart, Bar, LineChart, Line,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { Card, PageHeader, StatTile, Loader, ErrorMessage, EmptyMessage, ChartTooltip } from '../components.jsx';
import { getJson, toTitle, formatNumber, formatRupee, shortMonth, CHART_COLORS, AXIS_STYLE, GRID_COLOR } from '../helpers.js';
import './RoleSpecificAnalysis.css';

const CURRENT_YEAR = new Date().getFullYear();

function RoleSpecificAnalysis() {
    // Empty until the user picks a role; until then the first role in the list is shown.
    const [selectedRole, setSelectedRole] = useState('');

    const rolesQuery = useQuery({
        queryKey: ['topRoles', 'all', 5],
        queryFn: () => getJson('/api/top-role-table?field=all&limit=5'),
    });

    if (rolesQuery.isLoading) {
        return <Card title="Roles"><Loader /></Card>;
    }
    if (rolesQuery.isError) {
        return <Card title="Roles"><ErrorMessage /></Card>;
    }
    if (rolesQuery.data.length === 0) {
        return <Card title="Roles"><EmptyMessage text="No roles found." /></Card>;
    }

    let activeRole = selectedRole;
    if (activeRole === '') {
        activeRole = rolesQuery.data[0].role;
    }

    return (
        <>
            <PageHeader
                title="Role Analysis"
                description="A closer look at one role: postings, salary, skills and monthly activity."
            >
                <select
                    className="native-select"
                    value={activeRole}
                    onChange={(event) => setSelectedRole(event.target.value)}
                >
                    {rolesQuery.data.map((row) => (
                        <option key={row.role} value={row.role}>{toTitle(row.role)}</option>
                    ))}
                </select>
            </PageHeader>

            <RoleDetails role={activeRole} />
        </>
    );
}

// ---------- Everything for the selected role: /api/role-details ----------

function RoleDetails({ role }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['roleDetails', role],
        queryFn: () => getJson(`/api/role-details?role=${encodeURIComponent(role)}`),
    });

    if (isLoading) {
        return <Card><Loader /></Card>;
    }
    if (isError) {
        return <Card><ErrorMessage /></Card>;
    }

    let salaryText = 'Not available';
    if (data.average_salary !== null) {
        salaryText = formatRupee(data.average_salary);
    }

    return (
        <>
            <div className="role-stat-grid">
                <StatTile
                    label="Total postings recorded"
                    value={formatNumber(data.total_postings)}
                    meta={toTitle(data.role)}
                />
                <StatTile
                    label="Average salary"
                    value={salaryText}
                    meta="Midpoint of the salary range, per posting"
                />
            </div>

            <div className="grid-two">
                <TopSkillsChart skills={data.top_skills} />
                <MonthlyPostingsChart months={data.monthly_postings} />
            </div>
        </>
    );
}

// ---------- Most asked skills ----------

function TopSkillsChart({ skills }) {
    let body;
    if (skills.length === 0) {
        body = <EmptyMessage text="No skills recorded for this role." />;
    } else {
        body = (
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={skills} layout="vertical" margin={{ top: 0, right: 40, left: 0, bottom: 0 }}>
                    <CartesianGrid horizontal={false} stroke={GRID_COLOR} />
                    <XAxis type="number" {...AXIS_STYLE} />
                    <YAxis type="category" dataKey="skill" width={130} tickFormatter={toTitle} {...AXIS_STYLE} />
                    <Tooltip content={<ChartTooltip labelFormatter={toTitle} />} cursor={{ fill: '#f3f3f0' }} />
                    <Bar
                        dataKey="skill_count"
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
        <Card title="Most asked skills" subtitle="Top 5 skills by number of postings">
            {body}
        </Card>
    );
}

// ---------- Postings per month this year ----------

function MonthlyPostingsChart({ months }) {
    let body;
    if (months.length === 0) {
        body = <EmptyMessage text={`No postings for this role in ${CURRENT_YEAR}.`} />;
    } else {
        const chartData = months.map((row) => {
            return { month: shortMonth(row.month), postings: row.postings };
        });

        body = (
            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData} margin={{ top: 8, right: 16, left: -8, bottom: 0 }}>
                    <CartesianGrid vertical={false} stroke={GRID_COLOR} />
                    <XAxis dataKey="month" {...AXIS_STYLE} dy={8} />
                    <YAxis {...AXIS_STYLE} width={48} allowDecimals={false} />
                    <Tooltip content={<ChartTooltip />} />
                    <Line
                        type="monotone"
                        dataKey="postings"
                        name="Postings"
                        stroke={CHART_COLORS[1]}
                        strokeWidth={2}
                        dot={{ r: 3, strokeWidth: 0, fill: CHART_COLORS[1] }}
                        activeDot={{ r: 5, strokeWidth: 2, stroke: '#ffffff' }}
                    />
                </LineChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Card title="Monthly postings" subtitle={`Postings per month in ${CURRENT_YEAR}`}>
            {body}
        </Card>
    );
}

export default RoleSpecificAnalysis;
