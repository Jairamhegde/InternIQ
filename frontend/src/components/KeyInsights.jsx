import { API_URL } from '../config.js';
import { useQuery } from '@tanstack/react-query';
import "./KeyInsights.css"

import Loader from './Loader'

function Key_insights({ selectedYear, data, selectedField }) {
    const hasData = Object.keys(data || {}).length > 0;

    const { data: keydata = {}, isLoading } = useQuery({
        queryKey: ['keyInsights', selectedYear, selectedField?.value, data],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/job-posting-card-insights`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    year: selectedYear,
                    tile_data: data,
                    field: selectedField?.value || 'all'
                })
            });
            if (!response.ok) throw new Error("Failed to connect to job-posting-insighs endpoint");
            return response.json();
        },
        enabled: hasData
    });

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
