import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    BarChart, Bar, LineChart, Line,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import {
    PageLayout, Panel, Stat, ChipGroup, Loader, ErrorMessage, EmptyMessage, ChartTooltip,
} from '../components.jsx';
import {
    getJson, toTitle, formatNumber, formatRupee, shortMonth,
    CHART_COLORS, AXIS_STYLE, LABEL_COLOR, LABEL_TICK, GRID_COLOR, HOVER_CURSOR, ACTIVE_DOT_RING,
} from '../helpers.js';

const CURRENT_YEAR = new Date().getFullYear();

function RoleDetails() {
    const [role, setRole] = useState(null);

    const rolesQuery = useQuery({
        queryKey: ['roleOptions'],
        queryFn: () => getJson('/api/top-role-table'),
    });

    // select the most posted role
    useEffect(() => {
        if (rolesQuery.data && rolesQuery.data.length > 0 && role === null) {
            setRole(rolesQuery.data[0].role);
        }
    }, [rolesQuery.data, role]);

    let sidebar = <Loader />;
    if (rolesQuery.isError) {
        sidebar = <ErrorMessage text="Could not load roles." />;
    } else if (rolesQuery.data && role !== null) {
        const roleOptions = rolesQuery.data.map((row) => ({ value: row.role, label: toTitle(row.role) }));
        sidebar = <ChipGroup label="Role" options={roleOptions} value={role} onChange={setRole} />;
    }

    let title = 'Role details';
    if (role !== null) {
        title = toTitle(role);
    }

    let content = <Panel><Loader /></Panel>;
    if (rolesQuery.isError) {
        content = <Panel><ErrorMessage /></Panel>;
    } else if (role !== null) {
        content = <RoleBody role={role} />;
    }

    return (
        <PageLayout
            title={title}
            description="Openings, salary, skills and monthly hiring for one role."
            sidebar={sidebar}
            sidebarTitle="Filters"
        >
            {content}
        </PageLayout>
    );
}

// role details

function RoleBody({ role }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['roleDetails', role],
        queryFn: () => getJson(`/api/role-details?role=${encodeURIComponent(role)}`),
    });

    if (isLoading) {
        return <Panel><Loader /></Panel>;
    }
    if (isError) {
        return <Panel><ErrorMessage /></Panel>;
    }

    return (
        <>
            <RoleStats data={data} />
            <div className="row">
                <TopSkillsChart skills={data.top_skills} />
                <MonthlyPostingsChart months={data.monthly_postings} />
            </div>
        </>
    );
}

function RoleStats({ data }) {
    let salaryValue = 'Not available';
    let salaryMeta = 'Too few postings list a salary';
    if (data.average_salary !== null) {
        salaryValue = formatRupee(data.average_salary);
        salaryMeta = 'From postings that list a salary';
    }

    let skillValue = 'None yet';
    let skillMeta = '';
    if (data.top_skills.length > 0) {
        const topSkill = data.top_skills[0];
        const share = Math.round((topSkill.skill_count / data.total_postings) * 100);
        skillValue = toTitle(topSkill.skill);
        skillMeta = `In ${share}% of postings`;
    }

    return (
        <div className="stats stats-3">
            <Stat label="Postings recorded" value={formatNumber(data.total_postings)} meta="All postings collected so far" />
            <Stat label="Average salary" value={salaryValue} meta={salaryMeta} />
            <Stat label="Most asked skill" value={skillValue} meta={skillMeta} />
        </div>
    );
}

// top skills chart

function TopSkillsChart({ skills }) {
    let body;
    if (skills.length === 0) {
        body = <EmptyMessage title="No skills recorded for this role" />;
    } else {
        body = (
            <ResponsiveContainer width="100%" height={260}>
                <BarChart data={skills} layout="vertical" margin={{ top: 0, right: 44, left: 0, bottom: 0 }}>
                    <CartesianGrid horizontal={false} stroke={GRID_COLOR} />
                    <XAxis type="number" {...AXIS_STYLE} />
                    <YAxis type="category" dataKey="skill" width={130} tickFormatter={toTitle} {...AXIS_STYLE} tick={LABEL_TICK} />
                    <Tooltip content={<ChartTooltip labelFormatter={toTitle} />} cursor={HOVER_CURSOR} />
                    <Bar
                        isAnimationActive={false}
                        dataKey="skill_count"
                        name="Postings"
                        fill={CHART_COLORS[2]}
                        radius={[0, 4, 4, 0]}
                        maxBarSize={20}
                        label={{ position: 'right', fill: LABEL_COLOR, fontSize: 12 }}
                    />
                </BarChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Panel title="Most asked skills" subtitle="Top 5 skills by number of postings">
            {body}
        </Panel>
    );
}

// postings per month chart

function MonthlyPostingsChart({ months }) {
    let body;
    if (months.length === 0) {
        body = <EmptyMessage title={`No postings for this role in ${CURRENT_YEAR}`} />;
    } else {
        const chartData = months.map((row) => ({ month: shortMonth(row.month), postings: row.postings }));
        body = (
            <ResponsiveContainer width="100%" height={260}>
                <LineChart data={chartData} margin={{ top: 8, right: 16, left: -12, bottom: 0 }}>
                    <CartesianGrid vertical={false} stroke={GRID_COLOR} />
                    <XAxis dataKey="month" {...AXIS_STYLE} dy={8} />
                    <YAxis {...AXIS_STYLE} width={48} allowDecimals={false} />
                    <Tooltip content={<ChartTooltip />} cursor={{ stroke: GRID_COLOR }} />
                    <Line
                        isAnimationActive={false}
                        type="monotone"
                        dataKey="postings"
                        name="Postings"
                        stroke={CHART_COLORS[0]}
                        strokeWidth={2}
                        dot={{ r: 3, strokeWidth: 0, fill: CHART_COLORS[0] }}
                        activeDot={{ r: 5, strokeWidth: 2, stroke: ACTIVE_DOT_RING }}
                    />
                </LineChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Panel title="Postings per month" subtitle={String(CURRENT_YEAR)}>
            {body}
        </Panel>
    );
}

export default RoleDetails;
