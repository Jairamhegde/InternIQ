import { useState, useEffect } from 'react'
import "./KeyInsights.css"

function Key_insights({ selectedYear }) {

    const [data, setData] = useState({})

    useEffect(() => {
        fetch(`http://localhost:8000/api/job-posting-card-insights?year=${selectedYear}`)
            .then((Response) => Response.json())
            .then((jsonData => {
                setData(jsonData);
            }))
            .catch((error) => console.log("Failed to connect to job-posting-insighs endpoint", error))
    }, [selectedYear])


    return (
        <div className="insights-card">

            {/* Card Header */}
            <div className="insights-header">
                <span className="insights-icon">
                    <img src="/bulb.png" alt="insights" width="22" height="22" />
                </span>
                <h3>Key Insights</h3>
            </div>

            {/* Divider */}
            <div className="divider"></div>

            {/* Insight 1 */}
            <div className="insight">
                <h4>{data.brief || ""}</h4>
            </div>
            {/* Highlighted Insight */}
            <div className="highlighted-insight">
                <p>
                    {data.detail || ""}
                </p>
            </div>

        </div>
    );
}
export default Key_insights