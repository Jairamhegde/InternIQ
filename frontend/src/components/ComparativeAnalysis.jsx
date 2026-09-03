import { useState, useEffect } from 'react'
import { API_URL } from '../config.js';
import "./ComparativeAnalysis.css"
import Select from 'react-select';
import startCase from "lodash/startCase";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';

import {
    Radar,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,

} from 'recharts';
import {
    LineChart,
    Line,
    Legend,

} from 'recharts';

import { result } from 'lodash';
import Loader from './Loader';
import { useQuery } from '@tanstack/react-query';


function ComparativeAnalysis() {

    const { data: topRoles = [], isLoading } = useQuery({
        queryKey: ['topRolesSelect'],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/top-role-table`);
            if (!response.ok) throw new Error("Failed to connect to top-role endpoint");
            const result = await response.json();
            return result.map((item) => ({
                value: item.role,
                label: item.role,
            }));
        }
    });
    const [selectedJobs, setSelectedJobs] = useState([]);
    useEffect(() => {
        if (topRoles.length > 2 && selectedJobs.length === 0) {
            setSelectedJobs([topRoles[0], topRoles[1]]);

        }

    })
    return (
        <div className='comparative-analysis-page'>
            <div className='comparative-header'>
                <h1>Comparative Analysis</h1>
                <p>Compare multiple jobs across key metrics and trends</p>
            </div>
            <SelectBox selectedJobs={selectedJobs} setSelectedJobs
                ={setSelectedJobs} topRoles={topRoles} isLoading={isLoading} />

        </div>
    );
}


function SelectBox({ selectedJobs, setSelectedJobs, topRoles, isLoading }) {

    const handleChange = (selected) => {
        if (!selected || selected.length <= 3) {
            setSelectedJobs(selected || []);
        }
    };

    return (
        <div className="select-box-container">
            {isLoading ? (<Loader />) : (
                <>
                    <h3>
                        Select two or three job roles to compare
                    </h3>
                    <Select
                        options={topRoles}
                        isMulti
                        value={selectedJobs}
                        onChange={handleChange}
                        isOptionDisabled={() => selectedJobs.length >= 3}
                        placeholder="Search and select 2 to 3 roles..."
                    />
                    <div className="selection-status">
                        {selectedJobs.length < 2 ? (
                            <span className="status-hint warning">
                                Please select at least 2 roles (Selected: {selectedJobs.length}/3)
                            </span>
                        ) : (
                            <>
                                <span className="status-hint success">
                                    ✓ Ready for comparison ({selectedJobs.length}/3 selected)
                                </span>

                                <ComaparitiveCharts selectedJobs={selectedJobs} />
                            </>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
function ComaparitiveCharts({ selectedJobs }) {
    const roleNames = selectedJobs?.map(job => job.value || job) || [];
    const hasEnoughJobs = roleNames.length >= 2;

    const { data: commonSkills = [] } = useQuery({
        queryKey: ['commonSkills', roleNames],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/common-skill`, {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ roles: roleNames })
            });
            if (!response.ok) throw new Error("failed to connect to common skill endpoint");
            return response.json();
        },
        enabled: hasEnoughJobs
    });

    const { data: chartData = [] } = useQuery({
        queryKey: ['chartData', roleNames],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/get-role-posting`, {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ roles: roleNames })
            });
            if (!response.ok) throw new Error("Failed to connect to role posting endpoint");
            return response.json();
        },
        enabled: hasEnoughJobs
    });

    const hasDataForInsights = chartData.length > 0 && commonSkills.length > 0;

    const { data: compInsights = {} } = useQuery({
        queryKey: ['compInsights', chartData, commonSkills],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/get-comparative-insights`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    role_frequency: chartData,
                    common_skill: commonSkills
                })
            });
            if (!response.ok) throw new Error("Failed to connect to get-comparative-insights");
            return response.json();
        },
        enabled: hasDataForInsights
    });

    return (
        <div className='comparative-main'>
            <div className='comparative-dashboard'>
                <div className='comparative-chart'>
                    <div className='comp-header'>
                        <h3>Postings comparision</h3>
                    </div>
                    <ResponsiveContainer width="100%" height={350}>
                        <BarChart
                            data={chartData}
                            margin={{
                                top: 10,
                                left: 30,
                                right: 30,
                                bottom: 10
                            }}
                        >
                            <defs>
                                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#60a5fa" stopOpacity={1} />   /* Lighter Blue */
                                    <stop offset="100%" stopColor="#2e53b8ff" stopOpacity={1} />  /* Deep Blue */
                                </linearGradient>
                            </defs>
                            <XAxis dataKey='role' />
                            <YAxis />
                            <Tooltip labelFormatter={startCase}
                                contentStyle={{
                                    borderRadius: '12px',
                                    border: 'none',
                                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                                }}
                            />
                            <Bar dataKey="volume" fill="url(#barGradient)" radius={[6, 6, 0, 0]} animationDuration={1300}
                                label={{ position: 'top', fill: '#0f172a', fontSize: 13, fontWeight: 600 }} />

                        </BarChart>
                    </ResponsiveContainer>

                    <ComparativeAnalysisInsights title="Insights" data={compInsights?.role_insights} />
                </div>
                <div className='Radar-chart'>
                    <div className='comp-header'>
                        <h3>Skills Comparison</h3>
                    </div>
                    <ResponsiveContainer width='100%' height={350}>
                        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={commonSkills}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey='skill' tickFormatter={startCase} />
                            <PolarRadiusAxis angle={30} domain={[0, 100]} />
                            {
                                selectedJobs.map((job, index) => {
                                    const title = job.value || job
                                    const colors = ['#3b82f6', '#10b981', '#f59e0b'];

                                    return (
                                        <Radar
                                            dataKey={title}
                                            name={startCase(title)}
                                            key={title}
                                            stroke={colors[index % colors.length]}
                                            fill={colors[index % colors.length]}
                                            fillOpacity={0.4}
                                        />
                                    )
                                })
                            }
                        </RadarChart>
                    </ResponsiveContainer>
                    <ComparativeAnalysisInsights title="Insights" data={compInsights?.skill_insights} />

                </div>
            </div>
            <div className='line-chart-div'>
                <Compare_line_chart selectedJobs={selectedJobs} />
            </div>

            <ComparativeAnalysisInsights title="Key takeaway" data={compInsights?.takeaway} />

        </div>
    );
}

function ComparativeAnalysisInsights({ title, data }) {
    return (
        <div className='comp-insights-card'>
            <h3>{title}</h3>
            {data ? (
                <p>{data}</p>
            ) : (
                <p>...</p>
            )}
        </div>
    );
}


function Compare_line_chart({ selectedJobs }) {
    const { data: data, isLoading } = useQuery({
        queryKey: ["linechart-data", selectedJobs],
        queryFn: async () => {

            const rolesList = selectedJobs.map(job => job.value);

            const response = await fetch(`${API_URL}/api/get-linechart-data`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ selected_jobs: rolesList })
                }
            )
            if (!response.ok) {
                throw new Error("Failed to connect to linechart data.")

            }
            return response.json()
        }
    })

    if (isLoading) {
        return <div className="linechart-status-container"><Loader /></div>;
    }

    if (!data || data.length === 0) {
        return <div className="linechart-status-container empty">No data available for the selected roles</div>;
    }

    // Modern vibrant color palette
    const colours = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'];

    const allFields = Object.keys(data[0])

    const allRoles = allFields.filter(key => key != 'month')

    return (

        <ResponsiveContainer width="100%" height={450} className="modern-line-chart-container" >
            <LineChart
                data={data}
                margin={{ top: 20, right: 30, left: 10, bottom: 20 }}
            >
                <CartesianGrid vertical={false} stroke="#f1f5f9" strokeDasharray="4 4" />

                <XAxis 
                    dataKey='month' 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#64748b', fontSize: 13, fontWeight: 500 }}
                    dy={15}
                />
                
                <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 13, fontWeight: 500 }}
                    dx={-10}
                    tickFormatter={(value) => `${value >= 1000 ? (value/1000).toFixed(1) + 'k' : value}`}
                />
                
                <Tooltip 
                    contentStyle={{ 
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        borderRadius: '12px',
                        border: '1px solid #e2e8f0',
                        boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
                        padding: '12px 16px',
                        fontWeight: 500
                    }}
                    cursor={{ stroke: '#cbd5e1', strokeWidth: 1, strokeDasharray: '3 3' }}
                />
                
                <Legend 
                    verticalAlign='top' 
                    height={40}
                    iconType="circle"
                    wrapperStyle={{ paddingBottom: '20px', fontWeight: 600, color: '#334155' }}
                />

                {allRoles.map((key, index) => (
                    <Line
                        key={key}
                        type="monotone"
                        dataKey={key}
                        stroke={colours[index % colours.length]}
                        strokeWidth={3}
                        dot={{ r: 5, strokeWidth: 2, fill: '#ffffff', stroke: colours[index % colours.length] }}
                        activeDot={{ r: 8, strokeWidth: 0, fill: colours[index % colours.length], filter: 'drop-shadow(0px 4px 6px rgba(0,0,0,0.3))' }}
                        animationDuration={1500}
                    />
                ))}

            </LineChart>

        </ResponsiveContainer>
    );
}
export default ComparativeAnalysis;
