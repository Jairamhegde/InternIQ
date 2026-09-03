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

    if (loading) {
        return (
            <div className="job-posting">
                <Loader />
            </div>
        );
    }

    if (!data || data.length <= 0) {
        return (
            <div className="job-posting">
                <div className="job-header">
                    <h3>Job Postings Volume</h3>
                    <div className="year-buttons">
                        {years.map((year) => (
                            <button
                                key={year}
                                onClick={() => setSelectedYear(year)}
                                className={selectedYear === year ? 'active' : ''}
                            >
                                {year}
                            </button>
                        ))}
                    </div>
                </div>
                <div className="no-data-container">
                    <span className="no-data-text">No data available this year.</span>
                </div>
            </div>
        );
    }

    return (
        <div className="job-posting">
            <div className="job-header">
                <h3>Job Postings Volume</h3>
                <div className="year-buttons">
                    {years.map((year) => (
                        <button
                            key={year}
                            onClick={() => setSelectedYear(year)}
                            className={selectedYear === year ? 'active' : ''}
                        >
                            {year}
                        </button>
                    ))}
                </div>
            </div>

            <div className="job-container">
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
                            <linearGradient id="colorJobs" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#0bec65ff" stopOpacity={0.4} />
                                <stop offset="95%" stopColor="#25eb74ff" stopOpacity={0.0} />
                            </linearGradient>
                        </defs>

                        <CartesianGrid vertical={false} stroke="#e5e7eb" strokeDasharray="0" />

                        <XAxis
                            dataKey="month"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#6b7280', fontSize: 13 }}
                            dy={10}
                        />

                        <YAxis
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#6b7280', fontSize: 13 }}
                            tickFormatter={(value) => `${value === 0 ? 0 : value / 1000}k`}
                            domain={[0, 1000]}
                            ticks={[0, 100, 500, 1000, 5000]}
                        />

                        <Tooltip
                            contentStyle={{
                                borderRadius: '8px',
                                border: 'none',
                                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                            }}
                        />

                        <Area
                            type="monotone"
                            dataKey="jobs"
                            stroke="#17d181ff"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorJobs)"
                            dot={{ r: 6, fill: '#fff', stroke: '#1d4ed8', strokeWidth: 1.5 }}
                            activeDot={{ r: 8, fill: '#fff', stroke: '#1d4ed8', strokeWidth: 2 }}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}

export default JobPosting_chart;
