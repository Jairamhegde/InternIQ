import { useState, useEffect } from "react";
import "./RecentMarketTrend.css"
import { result, values } from "lodash";
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
import Loader from './Loader';


function RecentMarketTrend() {

    const [statsdata, setStatsData] = useState([])
    const [isLoading, setLoading] = useState(true)
    useEffect(() => {
        fetch(`http://localhost:8000/api/recent-market-trend`)
            .then((response) => response.json())
            .then((result) => { setStatsData(result); setLoading(false); })
            .catch((err) => { console.log("failed to connect to recent-market-trend"); setLoading(false); })
    }, [])
    const data = [
        {
            label: "TOTAL OPPORTUNITIES",
            value: statsdata?.postings
        },
        {
            label: "MOST DEMANDING SKILL",
            value: statsdata?.skill?.[0] || "Loading..."
        },
        {
            label: "DEMANDING ROLE",
            value: statsdata?.role?.[0] || "Loading..."
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
                                    <div className="stat-value-row">
                                        <h3 className="stat-value">{stat.value}</h3>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="chart-container">
                            <TrendsChart chartData={statsdata?.toproles} />
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
            <div className='comp-header'>
                <h3>Top Roles</h3>
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
                    <XAxis dataKey='role' tickFormatter={startCase} />
                    <YAxis />
                    <Tooltip labelFormatter={startCase} />
                    <Bar dataKey="volume" fill="#3c9affff"
                        label={{ position: 'top', fill: '#0f172a', fontSize: 7, fontWeight: 600 }} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}



export default RecentMarketTrend;

