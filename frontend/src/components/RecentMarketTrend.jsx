import { API_URL } from '../config.js';
import "./RecentMarketTrend.css"
import { result, values } from "lodash";
import startCase from "lodash/startCase";
import Loader from "./Loader";
import { useQuery } from '@tanstack/react-query';

import BuildingSvg from '../assets/building.svg'
import BriefCase from '../assets/briefcase.svg'






import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,

    PieChart,
    Pie,
    Legend,
    Sector

} from 'recharts';



function RecentMarketTrend() {
    const { data: statsdata = [], isLoading } = useQuery({
        queryKey: ['recentMarketTrend'],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/recent-market-trend`);
            if (!response.ok) throw new Error("failed to connect to recent-market-trend");
            return response.json();
        }
    });

    const data = [
        {
            label: "TOTAL OPPORTUNITIES",
            value: statsdata?.postings || "Loading..",
            increment: statsdata?.increment
        },
        {
            label: "MOST DEMANDING SKILL",
            value: statsdata?.skill?.[0] || "Loading..."
        },
        {
            label: "DEMANDING ROLE",
            value: statsdata?.role?.[0] || "Loading..."
        },
        {
            label: "TOP ROLE AVG STIPEND",
            value: statsdata?.average_sal ? `₹${Number(statsdata.average_sal).toLocaleString("en-IN")}` : "Loading..."
        },
        {
            label: "TOP LOCATION",
            value: statsdata?.toplocation?.[0] || "Loading..."
        },

    ]
    return (
        <div className="recent-market-trend">
            {isLoading ? (<Loader />) : (
                <>
                    <div className="rmt-header">
                        <h1>Recent Market Trends</h1>
                        <p>Last 10 days market analysis</p>
                    </div>
                    <div className="rmt-body">
                        <div className="overview-cards">
                            {data.map((stat, index) => (
                                <div className="stat-card" key={index}>
                                    <span className="stat-label">{startCase(stat.label)}</span>
                                    <div className="stat-value-row" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                        <h3 className="stat-value">{stat.value}</h3>

                                        {stat.increment !== undefined && (
                                            <span style={{
                                                fontSize: '0.85rem',
                                                fontWeight: '600',
                                                color: stat.increment > 0 ? '#16a34a' : (stat.increment < 0 ? '#dc2626' : '#64748b'),
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '2px',
                                                backgroundColor: stat.increment > 0 ? '#dcfce7' : (stat.increment < 0 ? '#fee2e2' : '#f1f5f9'),
                                                padding: '2px 8px',
                                                borderRadius: '12px'
                                            }}>
                                                {stat.increment > 0 ? '↑' : (stat.increment < 0 ? '↓' : '−')} {Math.abs(stat.increment)}%
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="loc-posting-chart">
                            <div className="chart-container">
                                <h4>Job Postings</h4>
                                <TrendsChart chartData={statsdata?.toproles} />

                            </div>
                            <div className="chart-container">
                                <h4>Top Locations</h4>
                                <TopLocationChart />
                            </div>
                        </div>


                        <div className="job-posting-table">
                            <RecentPostingList />
                        </div>

                    </div>
                </>
            )}
        </div>
    );
}


function TrendsChart({ chartData }) {
    return (
        <div className="barchart" >

            <ResponsiveContainer width="100%" height={350}>
                <BarChart
                    data={chartData}
                    margin={{
                        top: 10,
                        left: 30,
                        right: 30,
                        bottom: 10
                    }}>

                    <defs>
                        <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#60a5fa" stopOpacity={1} />
                            <stop offset="100%" stopColor="#2e53b8ff" stopOpacity={1} />
                        </linearGradient>
                    </defs>


                    <XAxis dataKey='role'
                        tickFormatter={startCase}
                        tickLine={false}
                        angle={-45}
                        textAnchor='end'
                        height={80}
                        tick={{ fontSize: 14 }} />
                    <YAxis />
                    <Tooltip
                        labelFormatter={startCase}
                        cursor={{ fill: '#f1f5f9' }}
                        contentStyle={{
                            borderRadius: '12px',
                            border: 'none',
                            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                        }}
                    />
                    <Bar dataKey="volume" fill="url(#barGradient)" radius={[6, 6, 0, 0]} animationDuration={1500}
                        label={{ position: 'top', fill: '#0f172a', fontSize: 7, fontWeight: 600 }} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}

function RecentPostingList() {
    const { data: jolListing = [] } = useQuery({
        queryKey: ['recentPostingList'],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/job-posting-list`);
            if (!response.ok) throw new Error("failed to connect to job-posting-list");
            const result = await response.json();
            return Array.isArray(result) ? result : [];
        }
    });

    return (
        <div className="top-roles-card">

            <>
                <div className="top-roles-header">
                    <h3>Recent Job Postings</h3>
                </div>

                <div className="table-responsive">
                    <table className="top-roles-table">
                        <thead>
                            <tr>
                                <th>Role Profile</th>
                                <th>Company</th>
                                <th>Posted Date</th>
                                <th className="align-right">Link</th>
                            </tr>
                        </thead>
                        <tbody>
                            {jolListing.map((item, index) => (
                                <tr key={index}>
                                    <td className="role-name">
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            <img src={BriefCase} alt="BriefCase" style={{ width: '16px', height: '16px', opacity: 0.7 }} />
                                            {startCase(item.title)}
                                        </div>
                                    </td>
                                    <td className="company-name">
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            <img src={BuildingSvg} alt="Building" style={{ width: '16px', height: '16px', opacity: 0.7 }} />
                                            {startCase(item.company)}
                                        </div>
                                    </td>
                                    <td className="company-name">{item.posted_date}</td>
                                    <td className="volume-val align-right">
                                        {item.job_link ? (
                                            <button onClick={() => window.open(item.job_link, "_blank")} className="link-button">Check</button>
                                        ) : (
                                            <span style={{ fontSize: "0.8rem", color: "#424242ff", display: "block" }}>
                                                Link unavailable
                                            </span>
                                        )}

                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </>

        </div>
    );



}

function TopLocationChart() {
    const { data: locData = [], isLoading } = useQuery({
        queryKey: ['topLocations'],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/get-top-locations`);
            if (!response.ok) throw new Error("failed to connect to get-top-locations");
            return response.json();
        }
    });

    return (

        <div className="piechart-container">
            {isLoading ? (<Loader />) : (

                <ResponsiveContainer width='100%' height={300}>
                    <PieChart>
                        <Pie
                            data={locData}
                            cx='50%'
                            cy='50%'
                            innerRadius={60}
                            outerRadius={100}
                            paddingAngle={5}
                            dataKey='value'
                            nameKey='name'
                            label={({ name, percent, x, y, textAnchor }) => (
                                <text x={x} y={y} textAnchor={textAnchor} fill="#0f172a" fontSize="12px" fontWeight="600">
                                    {`${startCase(name)} (${(percent * 100).toFixed(0)}%)`}
                                </text>
                            )}
                        />
                        <Tooltip />

                    </PieChart>
                </ResponsiveContainer>


            )}
        </div>
    )
}




export default RecentMarketTrend;

