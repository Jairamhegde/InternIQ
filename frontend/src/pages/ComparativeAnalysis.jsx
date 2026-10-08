import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Select from 'react-select';
import {
    BarChart, Bar, Cell, LineChart, Line, Legend,
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { Card, PageHeader, Loader, ErrorMessage, EmptyMessage, ChartTooltip } from '../components.jsx';
import { getJson, postJson, toTitle, shortMonth, formatRupee, CHART_COLORS, AXIS_STYLE, GRID_COLOR } from '../helpers.js';
import './ComparativeAnalysis.css';

const MIN_ROLES = 2;
const MAX_ROLES = 3;
const RADAR_SKILL_LIMIT = 10;

// One colour for every salary bar, so this chart does not look like the postings chart.
const SALARY_BAR_COLOR = '#5a9a78';

function ComparativeAnalysis() {
    const [selectedRoles, setSelectedRoles] = useState(null);
    const [roleColors, setRoleColors] = useState({});

    const rolesQuery = useQuery({
        queryKey: ['roleOptions'],
        queryFn: () => getJson('/api/top-role-table'),
    });

    // Select the first two roles once the role list has loaded.
    useEffect(() => {
        if (rolesQuery.data && rolesQuery.data.length >= MIN_ROLES && selectedRoles === null) {
            const firstTwo = [rolesQuery.data[0].role, rolesQuery.data[1].role];
            setSelectedRoles(firstTwo);
            setRoleColors(assignColors({}, firstTwo));
        }
    }, [rolesQuery.data, selectedRoles]);

    function handleRoleChange(newRoles) {
        setSelectedRoles(newRoles);
        setRoleColors(assignColors(roleColors, newRoles));
    }

    let body;
    if (rolesQuery.isLoading || selectedRoles === null) {
        body = <Card title="Roles"><Loader /></Card>;
    } else if (rolesQuery.isError) {
        body = <Card title="Roles"><ErrorMessage /></Card>;
    } else {
        body = (
            <>
                <RolePicker
                    allRoles={rolesQuery.data}
                    selectedRoles={selectedRoles}
                    onChange={handleRoleChange}
                />
                {selectedRoles.length < MIN_ROLES ? (
                    <div className="compare-empty">Select at least two roles to see the comparison.</div>
                ) : (
                    <ComparisonCharts selectedRoles={selectedRoles} roleColors={roleColors} />
                )}
            </>
        );
    }

    return (
        <>
            <PageHeader
                title="Compare Roles"
                description="Compare two or three roles on postings, skills, monthly trend and salary."
            />
            {body}
        </>
    );
}

// Keeps each selected role's colour stable when other roles are added or removed.
function assignColors(oldColors, roles) {
    const newColors = {};
    const usedColors = [];

    for (const role of roles) {
        if (oldColors[role]) {
            newColors[role] = oldColors[role];
            usedColors.push(oldColors[role]);
        }
    }

    for (const role of roles) {
        if (!newColors[role]) {
            const freeColor = CHART_COLORS.find((color) => !usedColors.includes(color));
            newColors[role] = freeColor;
            usedColors.push(freeColor);
        }
    }

    return newColors;
}

// ---------- Role picker ----------

function RolePicker({ allRoles, selectedRoles, onChange }) {
    const options = allRoles.map((row) => ({ value: row.role, label: toTitle(row.role) }));
    const selectedOptions = options.filter((option) => selectedRoles.includes(option.value));

    function handleChange(chosenOptions) {
        const roles = chosenOptions.map((option) => option.value);
        if (roles.length <= MAX_ROLES) {
            onChange(roles);
        }
    }

    return (
        <Card title="Roles" action={<span className="picker-count">{selectedRoles.length} of {MAX_ROLES} selected</span>}>
            <Select
                options={options}
                value={selectedOptions}
                onChange={handleChange}
                isMulti
                isOptionDisabled={() => selectedRoles.length >= MAX_ROLES}
                placeholder="Search and select 2 to 3 roles..."
                classNamePrefix="role-select"
            />
        </Card>
    );
}

// ---------- All comparison charts ----------

function ComparisonCharts({ selectedRoles, roleColors }) {
    const postingsQuery = useQuery({
        queryKey: ['rolePostings', selectedRoles],
        queryFn: () => postJson('/api/get-role-posting', { roles: selectedRoles }),
    });

    const skillsQuery = useQuery({
        queryKey: ['commonSkills', selectedRoles],
        queryFn: () => postJson('/api/common-skill', { roles: selectedRoles }),
    });

    return (
        <>
            <div className="compare-grid">
                <PostingsChart query={postingsQuery} roleColors={roleColors} />
                <SkillsRadar query={skillsQuery} selectedRoles={selectedRoles} roleColors={roleColors} />
            </div>
            <MonthlyTrendChart selectedRoles={selectedRoles} roleColors={roleColors} />
            <SalaryChart query={postingsQuery} />
            <KeyTakeaway postings={postingsQuery.data} skills={skillsQuery.data} />
        </>
    );
}

// ---------- Postings comparison: /api/get-role-posting ----------

function PostingsChart({ query, roleColors }) {
    let body;
    if (query.isLoading) {
        body = <Loader />;
    } else if (query.isError) {
        body = <ErrorMessage />;
    } else if (query.data.length === 0) {
        body = <EmptyMessage />;
    } else {
        body = (
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={query.data} margin={{ top: 20, right: 8, left: -8, bottom: 0 }} barCategoryGap="30%">
                    <CartesianGrid vertical={false} stroke={GRID_COLOR} />
                    <XAxis dataKey="role" tickFormatter={toTitle} interval={0} {...AXIS_STYLE} dy={8} />
                    <YAxis {...AXIS_STYLE} width={48} />
                    <Tooltip content={<ChartTooltip labelFormatter={toTitle} />} cursor={{ fill: '#f3f3f0' }} />
                    <Bar
                        dataKey="volume"
                        name="Postings"
                        radius={[4, 4, 0, 0]}
                        maxBarSize={56}
                        label={{ position: 'top', fill: '#57564f', fontSize: 12 }}
                    >
                        {query.data.map((row) => (
                            <Cell key={row.role} fill={roleColors[row.role]} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Card title="Postings comparison" subtitle="Total postings per role">
            {body}
        </Card>
    );
}

// ---------- Skills comparison: /api/common-skill ----------

function SkillsRadar({ query, selectedRoles, roleColors }) {
    let body;
    if (query.isLoading) {
        body = <Loader />;
    } else if (query.isError) {
        body = <ErrorMessage />;
    } else if (query.data.length === 0) {
        body = <EmptyMessage />;
    } else {
        const topSkills = pickTopSkills(query.data, selectedRoles);
        body = (
            <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={topSkills} outerRadius="72%">
                    <PolarGrid stroke={GRID_COLOR} />
                    <PolarAngleAxis dataKey="skill" tickFormatter={toTitle} tick={{ fill: '#57564f', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#8b8a83', fontSize: 10 }} axisLine={false} />
                    <Tooltip content={<ChartTooltip labelFormatter={toTitle} valueSuffix="%" />} />
                    <Legend formatter={legendText} iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12 }} />
                    {selectedRoles.map((role) => (
                        <Radar
                            key={role}
                            dataKey={role}
                            name={toTitle(role)}
                            stroke={roleColors[role]}
                            fill={roleColors[role]}
                            fillOpacity={0.15}
                            strokeWidth={2}
                        />
                    ))}
                </RadarChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Card title="Skills comparison" subtitle={`Top ${RADAR_SKILL_LIMIT} skills, share of postings mentioning each (%)`}>
            {body}
        </Card>
    );
}

// Keeps only the skills with the highest combined share, so the radar stays readable.
function pickTopSkills(skillRows, selectedRoles) {
    const rowsWithTotal = skillRows.map((row) => {
        let total = 0;
        for (const role of selectedRoles) {
            total = total + Number(row[role] || 0);
        }
        return { row: row, total: total };
    });

    rowsWithTotal.sort((first, second) => second.total - first.total);

    const topRows = rowsWithTotal.slice(0, RADAR_SKILL_LIMIT);
    return topRows.map((item) => item.row);
}

// ---------- Monthly trend: /api/get-linechart-data ----------

function MonthlyTrendChart({ selectedRoles, roleColors }) {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['monthlyTrend', selectedRoles],
        queryFn: () => postJson('/api/get-linechart-data', { selected_jobs: selectedRoles }),
    });

    let body;
    if (isLoading) {
        body = <Loader />;
    } else if (isError) {
        body = <ErrorMessage />;
    } else if (data.length === 0) {
        body = <EmptyMessage text="No monthly data for the selected roles." />;
    } else {
        const chartData = data.map((row) => ({ ...row, month: shortMonth(row.month) }));
        body = (
            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData} margin={{ top: 8, right: 16, left: -8, bottom: 0 }}>
                    <CartesianGrid vertical={false} stroke={GRID_COLOR} />
                    <XAxis dataKey="month" {...AXIS_STYLE} dy={8} />
                    <YAxis {...AXIS_STYLE} width={48} />
                    <Tooltip content={<ChartTooltip />} />
                    <Legend formatter={legendText} iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
                    {selectedRoles.map((role) => (
                        <Line
                            key={role}
                            type="monotone"
                            dataKey={role}
                            name={toTitle(role)}
                            stroke={roleColors[role]}
                            strokeWidth={2}
                            dot={{ r: 3, strokeWidth: 0, fill: roleColors[role] }}
                            activeDot={{ r: 5, strokeWidth: 2, stroke: '#ffffff' }}
                        />
                    ))}
                </LineChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Card title="Monthly postings" subtitle="New postings per month for each role">
            {body}
        </Card>
    );
}

// Legend text stays grey; the coloured dot next to it shows which line is which.
function legendText(value) {
    return <span className="legend-text">{value}</span>;
}

// ---------- Average salary: /api/get-role-posting (same response as the postings chart) ----------

function SalaryChart({ query }) {
    let body;
    if (query.isLoading) {
        body = <Loader />;
    } else if (query.isError) {
        body = <ErrorMessage />;
    } else {
        // Roles without any salary data come back with average_salary set to null.
        const rolesWithSalary = [];
        for (const row of query.data) {
            if (row.average_salary !== null) {
                rolesWithSalary.push(row);
            }
        }

        if (rolesWithSalary.length === 0) {
            body = <EmptyMessage text="No salary data for the selected roles." />;
        } else {
            body = (
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={rolesWithSalary} margin={{ top: 20, right: 8, left: 8, bottom: 0 }} barCategoryGap="30%">
                        <CartesianGrid vertical={false} stroke={GRID_COLOR} />
                        <XAxis dataKey="role" tickFormatter={toTitle} interval={0} {...AXIS_STYLE} dy={8} />
                        <YAxis tickFormatter={formatRupee} {...AXIS_STYLE} width={80} />
                        <Tooltip content={<ChartTooltip labelFormatter={toTitle} />} cursor={{ fill: '#f3f3f0' }} />
                        <Bar
                            dataKey="average_salary"
                            name="Average salary (₹)"
                            fill={SALARY_BAR_COLOR}
                            radius={[4, 4, 0, 0]}
                            maxBarSize={56}
                            label={{ position: 'top', fill: '#57564f', fontSize: 12, formatter: formatRupee }}
                        />
                    </BarChart>
                </ResponsiveContainer>
            );
        }
    }

    return (
        <Card title="Average salary" subtitle="Average of the salary range across postings for each role">
            {body}
        </Card>
    );
}

// ---------- AI takeaway: /api/get-comparative-insights ----------

function KeyTakeaway({ postings, skills }) {
    const hasData = Boolean(postings && postings.length > 0 && skills && skills.length > 0);

    const { data, isLoading, isError } = useQuery({
        queryKey: ['comparativeInsights', postings, skills],
        queryFn: () => postJson('/api/get-comparative-insights', { role_frequency: postings, common_skill: skills }),
        enabled: hasData,
    });

    let text = 'Waiting for chart data...';
    if (hasData && isLoading) {
        text = 'Generating takeaway...';
    }
    if (isError || (data && data.error)) {
        text = 'Insights are currently not available.';
    }
    if (data && data.takeaway) {
        text = data.takeaway;
    }

    return (
        <Card title="Key takeaway" subtitle="Generated by AI from the charts above">
            <p className="takeaway-text">{text}</p>
        </Card>
    );
}

export default ComparativeAnalysis;
