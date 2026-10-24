import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    BarChart, Bar, Cell, LineChart, Line, Legend,
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import {
    PageLayout, Panel, MultiChipGroup, Loader, ErrorMessage, EmptyMessage, ChartTooltip,
} from '../components.jsx';
import {
    getJson, postJson, toTitle, formatRupee, shortMonth, SALARY_NOTE,
    CHART_COLORS, AXIS_STYLE, LABEL_COLOR, LABEL_TICK, GRID_COLOR, HOVER_CURSOR, ACTIVE_DOT_RING,
} from '../helpers.js';

const MIN_ROLES = 2;
const MAX_ROLES = 3;
const RADAR_SKILL_LIMIT = 8;
const ROLE_COLORS = [CHART_COLORS[0], CHART_COLORS[1], CHART_COLORS[2]];

function CompareRoles() {
    const [selectedRoles, setSelectedRoles] = useState(null);
    const [roleColors, setRoleColors] = useState({});

    const rolesQuery = useQuery({
        queryKey: ['roleOptions'],
        queryFn: () => getJson('/api/top-role-table'),
    });

    // select the first three roles
    useEffect(() => {
        if (rolesQuery.data && selectedRoles === null) {
            const firstRoles = [];
            for (const row of rolesQuery.data.slice(0, MAX_ROLES)) {
                firstRoles.push(row.role);
            }
            setSelectedRoles(firstRoles);
            setRoleColors(assignColors({}, firstRoles));
        }
    }, [rolesQuery.data, selectedRoles]);

    function handleRoleChange(newRoles) {
        setSelectedRoles(newRoles);
        setRoleColors(assignColors(roleColors, newRoles));
    }

    let sidebar = <Loader />;
    let content = <Panel><Loader /></Panel>;

    if (rolesQuery.isError) {
        sidebar = <ErrorMessage text="Could not load roles." />;
        content = <Panel><ErrorMessage /></Panel>;
    } else if (rolesQuery.data && selectedRoles !== null) {
        const roleOptions = rolesQuery.data.map((row) => ({ value: row.role, label: toTitle(row.role) }));

        sidebar = (
            <MultiChipGroup
                label="Roles"
                hint="Pick 2 or 3 roles to compare."
                options={roleOptions}
                values={selectedRoles}
                max={MAX_ROLES}
                colors={roleColors}
                onChange={handleRoleChange}
            />
        );

        if (selectedRoles.length < MIN_ROLES) {
            content = <Panel><EmptyMessage title="Pick at least 2 roles" text="Choose roles in the filters to compare them." /></Panel>;
        } else {
            content = <Comparison selectedRoles={selectedRoles} roleColors={roleColors} />;
        }
    }

    return (
        <PageLayout
            title="Compare roles"
            description="See how roles differ in openings, skills, monthly hiring and salary."
            sidebar={sidebar}
            sidebarTitle="Filters"
        >
            {content}
        </PageLayout>
    );
}

// keep role colours stable
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
            const freeColor = ROLE_COLORS.find((color) => !usedColors.includes(color));
            newColors[role] = freeColor;
            usedColors.push(freeColor);
        }
    }

    return newColors;
}

// sort rows by selected roles
function sortBySelection(rows, selectedRoles) {
    const sorted = [...rows];
    sorted.sort((first, second) => selectedRoles.indexOf(first.role) - selectedRoles.indexOf(second.role));
    return sorted;
}

// comparison charts

function Comparison({ selectedRoles, roleColors }) {
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
            <div className="row">
                <PostingsChart query={postingsQuery} selectedRoles={selectedRoles} roleColors={roleColors} />
                <SalaryChart query={postingsQuery} selectedRoles={selectedRoles} roleColors={roleColors} />
            </div>
            <div className="row">
                <SkillsRadar query={skillsQuery} selectedRoles={selectedRoles} roleColors={roleColors} />
                <MonthlyChart selectedRoles={selectedRoles} roleColors={roleColors} />
            </div>
            <KeyTakeaway postings={postingsQuery.data} skills={skillsQuery.data} />
        </>
    );
}

// postings chart

function PostingsChart({ query, selectedRoles, roleColors }) {
    let body;
    if (query.isLoading) {
        body = <Loader />;
    } else if (query.isError) {
        body = <ErrorMessage />;
    } else if (query.data.length === 0) {
        body = <EmptyMessage title="No postings found" />;
    } else {
        const rows = sortBySelection(query.data, selectedRoles);
        body = (
            <ResponsiveContainer width="100%" height={260}>
                <BarChart data={rows} margin={{ top: 22, right: 8, left: -12, bottom: 0 }} barCategoryGap="28%">
                    <CartesianGrid vertical={false} stroke={GRID_COLOR} />
                    <XAxis dataKey="role" tickFormatter={toTitle} interval={0} {...AXIS_STYLE} dy={8} />
                    <YAxis {...AXIS_STYLE} width={48} />
                    <Tooltip content={<ChartTooltip labelFormatter={toTitle} />} cursor={HOVER_CURSOR} />
                    <Bar
                        isAnimationActive={false}
                        dataKey="volume"
                        name="Postings"
                        radius={[4, 4, 0, 0]}
                        maxBarSize={52}
                        label={{ position: 'top', fill: LABEL_COLOR, fontSize: 12 }}
                    >
                        {rows.map((row) => (
                            <Cell key={row.role} fill={roleColors[row.role]} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Panel title="Postings" subtitle="Total postings per role">
            {body}
        </Panel>
    );
}

// average salary chart

function SalaryChart({ query, selectedRoles, roleColors }) {
    let body;
    if (query.isLoading) {
        body = <Loader />;
    } else if (query.isError) {
        body = <ErrorMessage />;
    } else {
        const rows = sortBySelection(query.data, selectedRoles);

        // roles without salary data
        const rolesWithSalary = [];
        const rolesWithoutSalary = [];
        for (const row of rows) {
            if (row.average_salary === null) {
                rolesWithoutSalary.push(toTitle(row.role));
            } else {
                rolesWithSalary.push(row);
            }
        }

        if (rolesWithSalary.length === 0) {
            body = <EmptyMessage title="No salary data" text="None of these roles has enough postings that list a salary." />;
        } else {
            const chartHeight = rolesWithSalary.length * 56 + 20;

            let missingNote = null;
            if (rolesWithoutSalary.length > 0) {
                missingNote = <p className="chart-note">{rolesWithoutSalary.join(', ')}: too few postings list a salary.</p>;
            }

            body = (
                <>
                    <ResponsiveContainer width="100%" height={chartHeight}>
                        <BarChart data={rolesWithSalary} layout="vertical" margin={{ top: 0, right: 100, left: 0, bottom: 0 }}>
                            <XAxis type="number" hide />
                            <YAxis type="category" dataKey="role" width={150} tickFormatter={toTitle} {...AXIS_STYLE} tick={LABEL_TICK} />
                            <Tooltip content={<ChartTooltip labelFormatter={toTitle} valueFormatter={formatRupee} />} cursor={HOVER_CURSOR} />
                            <Bar
                                isAnimationActive={false}
                                dataKey="average_salary"
                                name="Average salary"
                                radius={[0, 4, 4, 0]}
                                maxBarSize={22}
                                label={{ position: 'right', fill: LABEL_COLOR, fontSize: 12, formatter: formatRupee }}
                            >
                                {rolesWithSalary.map((row) => (
                                    <Cell key={row.role} fill={roleColors[row.role]} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                    {missingNote}
                    <p className="chart-note">{SALARY_NOTE}</p>
                </>
            );
        }
    }

    return (
        <Panel title="Average salary" subtitle="Midpoint of the listed range, per year">
            {body}
        </Panel>
    );
}

// skills in common chart

function SkillsRadar({ query, selectedRoles, roleColors }) {
    let body;
    if (query.isLoading) {
        body = <Loader />;
    } else if (query.isError) {
        body = <ErrorMessage />;
    } else if (query.data.length === 0) {
        body = <EmptyMessage title="No shared skills" text="These roles have no skills in common." />;
    } else {
        const topSkills = pickTopSkills(query.data, selectedRoles);
        body = (
            <ResponsiveContainer width="100%" height={320}>
                <RadarChart data={topSkills} outerRadius="70%">
                    <PolarGrid stroke={GRID_COLOR} />
                    <PolarAngleAxis dataKey="skill" tickFormatter={toTitle} tick={{ fill: LABEL_COLOR, fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#7d8a9b', fontSize: 10 }} axisLine={false} />
                    <Tooltip content={<ChartTooltip labelFormatter={toTitle} valueFormatter={formatPercent} />} />
                    {selectedRoles.map((role) => (
                        <Radar
                            isAnimationActive={false}
                            key={role}
                            dataKey={role}
                            name={toTitle(role)}
                            stroke={roleColors[role]}
                            fill={roleColors[role]}
                            fillOpacity={0.14}
                            strokeWidth={2}
                        />
                    ))}
                </RadarChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Panel title="Skills in common" subtitle="Share of each role's postings that ask for the skill">
            {body}
        </Panel>
    );
}

// top skills for the radar chart
function pickTopSkills(skillRows, selectedRoles) {
    const rowsWithTotal = [];
    for (const row of skillRows) {
        let total = 0;
        for (const role of selectedRoles) {
            total = total + Number(row[role] || 0);
        }
        rowsWithTotal.push({ row: row, total: total });
    }

    rowsWithTotal.sort((first, second) => second.total - first.total);

    const topRows = [];
    for (const item of rowsWithTotal.slice(0, RADAR_SKILL_LIMIT)) {
        topRows.push(item.row);
    }
    return topRows;
}

function formatPercent(value) {
    return `${Math.round(value)}%`;
}

// postings per month chart

function MonthlyChart({ selectedRoles, roleColors }) {
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
        body = <EmptyMessage title="No monthly data" text="These roles have no postings this year." />;
    } else {
        const chartData = data.map((row) => ({ ...row, month: shortMonth(row.month) }));
        body = (
            <ResponsiveContainer width="100%" height={320}>
                <LineChart data={chartData} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
                    <CartesianGrid vertical={false} stroke={GRID_COLOR} />
                    <XAxis dataKey="month" {...AXIS_STYLE} dy={8} />
                    <YAxis {...AXIS_STYLE} width={48} allowDecimals={false} />
                    <Tooltip content={<ChartTooltip />} cursor={{ stroke: GRID_COLOR }} />
                    <Legend formatter={legendText} iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
                    {selectedRoles.map((role) => (
                        <Line
                            isAnimationActive={false}
                            key={role}
                            type="monotone"
                            dataKey={role}
                            name={toTitle(role)}
                            stroke={roleColors[role]}
                            strokeWidth={2}
                            dot={{ r: 3, strokeWidth: 0, fill: roleColors[role] }}
                            activeDot={{ r: 5, strokeWidth: 2, stroke: ACTIVE_DOT_RING }}
                        />
                    ))}
                </LineChart>
            </ResponsiveContainer>
        );
    }

    return (
        <Panel title="Postings per month" subtitle="New postings per month for each role">
            {body}
        </Panel>
    );
}

// legend text colour
function legendText(value) {
    return <span style={{ color: LABEL_COLOR }}>{value}</span>;
}

// ai takeaway

function KeyTakeaway({ postings, skills }) {
    const hasData = Boolean(postings && postings.length > 0 && skills && skills.length > 0);

    const { data, isLoading, isError } = useQuery({
        queryKey: ['comparativeInsights', postings, skills],
        queryFn: () => postJson('/api/get-comparative-insights', { role_frequency: postings, common_skill: skills }),
        enabled: hasData,
    });

    let text = 'Waiting for chart data...';
    if (hasData && isLoading) {
        text = 'Writing the takeaway...';
    }
    if (isError || (data && data.error)) {
        text = 'The takeaway is not available right now.';
    }
    if (data && data.takeaway) {
        text = data.takeaway;
    }

    return (
        <Panel title="Key takeaway" subtitle="Written by AI from the charts above" className="takeaway">
            <p>{text}</p>
        </Panel>
    );
}

export default CompareRoles;
