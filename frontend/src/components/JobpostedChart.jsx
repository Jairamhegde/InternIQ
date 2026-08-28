import { useState } from 'react';
import { API_URL } from '../config.js';
import { useQuery } from '@tanstack/react-query';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';

import './JobpostedChart.css';
import Loader from './Loader';

function JobPosting_chart({ selectedYear, setSelectedYear, selectedField }) {
    const years = [
        new Date().getFullYear() - 2,
        new Date().getFullYear() - 1,
        new Date().getFullYear()
    ];

    const { data = [], isLoading: loading } = useQuery({
        queryKey: ['jobPostings', selectedYear, selectedField?.value],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/job-postings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ year: selectedYear, field: selectedField?.value || 'all' })
            });
            if (!response.ok) throw new Error('Failed to connect to the endpoint');
            return response.json();
        }
    });

    return (
        <div
            className="job-posting"
            style={{
                background: '#fff',
                padding: '24px',
                borderRadius: '12px',
                border: '1px solid #e5e7eb'
            }}
        >
            {loading ? (
                <Loader />
            ) : (
                <>
                    <div
                        className="job-header"
                        style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '24px'
                        }}
                    >
                        <h3
                            style={{
                                margin: 0,
                                fontSize: '20px',
                                color: '#111827',
                                fontWeight: '600'
                            }}
                        >
                            Job Postings Volume
                        </h3>

                        <div
                            className="year-buttons"
                            style={{
                                display: 'flex',
                                gap: '8px'
                            }}
                        >
                            {years.map((year) => (
                                <button
                                    key={year}
                                    onClick={() => setSelectedYear(year)}
                                    style={{
                                        padding: '4px 12px',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '4px',
                                        fontSize: '13px',
                                        cursor: 'pointer',
                                        background:
                                            selectedYear === year
                                                ? '#2574ebff'
                                                : 'white',
                                        color:
                                            selectedYear === year
                                                ? 'white'
                                                : '#4b5563'
                                    }}
                                >
                                    {year}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div
                        className="job-container"
                        style={{
                            height: '320px',
                            width: '100%',
                            background: '#fafafa',
                            borderRadius: '8px',
                            padding: '20px 10px 10px 0',
                            border: '1px solid #f3f4f6'
                        }}
                    >
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart
                                data={data}
                                margin={{
                                    top: 10,
                                    right: 30,
                                    left: -10,
                                    bottom: 0
                                }}
                            >
                                <defs>
                                    <linearGradient
                                        id="colorJobs"
                                        x1="0"
                                        y1="0"
                                        x2="0"
                                        y2="1"
                                    >
                                        <stop
                                            offset="5%"
                                            stopColor="#0bec65ff"
                                            stopOpacity={0.4}
                                        />
                                        <stop
                                            offset="95%"
                                            stopColor="#25eb74ff"
                                            stopOpacity={0.0}
                                        />
                                    </linearGradient>
                                </defs>

                                <CartesianGrid
                                    vertical={false}
                                    stroke="#e5e7eb"
                                    strokeDasharray="0"
                                />

                                <XAxis
                                    dataKey="month"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{
                                        fill: '#6b7280',
                                        fontSize: 13
                                    }}
                                    dy={10}
                                />

                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{
                                        fill: '#6b7280',
                                        fontSize: 13
                                    }}
                                    tickFormatter={(value) =>
                                        `${value === 0 ? 0 : value / 1000}k`
                                    }
                                    domain={[0, 1000]}
                                    ticks={[0, 100, 500, 1000, 5000]}
                                />

                                <Tooltip
                                    contentStyle={{
                                        borderRadius: '8px',
                                        border: 'none',
                                        boxShadow:
                                            '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                                    }}
                                />

                                <Area
                                    type="monotone"
                                    dataKey="jobs"
                                    stroke="#17d181ff"
                                    strokeWidth={2}
                                    fillOpacity={1}
                                    fill="url(#colorJobs)"
                                    dot={{
                                        r: 6,
                                        fill: '#fff',
                                        stroke: '#1d4ed8',
                                        strokeWidth: 1.5
                                    }}
                                    activeDot={{
                                        r: 8,
                                        fill: '#fff',
                                        stroke: '#1d4ed8',
                                        strokeWidth: 2
                                    }}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </>
            )}
        </div>
    );
}

export default JobPosting_chart;
