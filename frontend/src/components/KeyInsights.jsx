import { useState, useEffect } from 'react'
import "./KeyInsights.css"

import Loader from './Loader'

function Key_insights({ selectedYear, data, selectedField }) {

    const [keydata, setData] = useState({})
    const [isLoading, setLoading] = useState(true)

    useEffect(() => {
        if (Object.keys(data).length === 0) {
            return;
        }
        setLoading(true);
        fetch(`http://localhost:8000/api/job-posting-card-insights`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(
                    {
                        year: selectedYear,
                        tile_data: data,
                        field: selectedField?.value || 'all'
                    }
                )
            }
        )
            .then((Response) => Response.json())
            .then((jsonData => {
                setData(jsonData);
                setLoading(false)
            }))
            .catch((error) => { console.log("Failed to connect to job-posting-insighs endpoint", error), setLoading(false) })
    }, [selectedYear, data, selectedField])

    return (
        <div className="insights-card">
            {isLoading ? (<Loader />) : (
                <>

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
                        <h4>{keydata.brief || ""}</h4>
                    </div>
                    {/* Highlighted Insight */}
                    <div className="highlighted-insight">
                        <p>
                            {keydata.detail || ""}
                        </p>
                    </div>
                    <div className="detail">
                        <p>
                            {keydata.overview || ""}
                        </p>
                    </div>
                </>

            )}
        </div>

    );
}
export default Key_insights