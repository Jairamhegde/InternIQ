import { useState, useEffect } from 'react'
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';
import "./JobpostedChart.css";

function JobPosting_chart({ selectedYear, setSelectedYear }) {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const years = [new Date().getFullYear() - 2, new Date().getFullYear() - 1, new Date().getFullYear()];


    useEffect(() => {
        fetch(`http://localhost:8000/api/job-postings?year=${selectedYear}`)
            .then((response) => response.json())
            .then((fetchData) => { setData(fetchData); setLoading(false); })
            .catch((error) => {
                console.log("Failed to connect to the endpoint", error);
                setLoading(false);
            })
    }, [selectedYear]);


    return (
        <div className="job-posting" style={{ background: '#fff', padding: '24px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
            {/* Header section with title and tags */}
            <div className="job-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>

                <h3 style={{ margin: 0, fontSize: '20px', color: '#111827', fontWeight: '600' }}>
                    Job Postings Volume
                </h3>
                <div className='year-buttons' style={{ display: 'flex', gap: '8px' }}>

                    {years.map((year) => (
                        <button key={year}
                            onClick={() => setSelectedYear(year)}
                            style={{
                                padding: "4px 12px",
                                border: "1px solid #e5e7eb",
                                borderRadius: "4px",
                                fontSize: "13px",
                                cursor: "pointer",
                                background:
                                    selectedYear === year
                                        ? "#2563eb"
                                        : "white",
                                color:
                                    selectedYear === year
                                        ? "white"
                                        : "#4b5563"
                            }}
                        >{year}</button>
                    ))}
                </div>
            </div>
            {/* Chart section with a light gray background just like the image */}
            <div className='job-container' style={{ height: '320px', width: '100%', background: '#fafafa', borderRadius: '8px', padding: '20px 10px 10px 0', border: '1px solid #f3f4f6' }}>
                <ResponsiveContainer width='100%' height='100%'>
                    <AreaChart data={data} margin={{ top: 10, right: 30, left: -10, bottom: 0 }}>
                        {/* Define the gradient for the area under the curve */}
                        <defs>
                            <linearGradient id="colorJobs" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.4} />
                                <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0} />
                            </linearGradient>
                        </defs>

                        {/* Light horizontal grid lines */}
                        <CartesianGrid vertical={false} stroke="#e5e7eb" strokeDasharray="0" />

                        {/* X-Axis styling */}
                        <XAxis
                            dataKey="month"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#6b7280', fontSize: 13 }}
                            dy={10}
                        />

                        {/* Y-Axis styling - custom formatter to add 'k' */}
                        <YAxis
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#6b7280', fontSize: 13 }}
                            tickFormatter={(value) => `${value === 0 ? 0 : value / 1000}k`}
                            domain={[0, 10000]}
                            ticks={[0, 100, 500, 1000, 5000]}
                        />
                        <Tooltip
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        />
                        {/* The actual curve and gradient area */}
                        <Area
                            type="monotone"
                            dataKey="jobs"
                            stroke="#1d4ed8" /* Darker blue line */
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorJobs)"

                            /* Adding the white dots with blue borders on data points */
                            dot={{ r: 6, fill: "#fff", stroke: "#1d4ed8", strokeWidth: 1.5 }}
                            activeDot={{ r: 8, fill: "#fff", stroke: "#1d4ed8", strokeWidth: 2 }}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}

export default JobPosting_chart;
