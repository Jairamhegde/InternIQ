import { API_URL } from '../config.js';
import { useQuery } from '@tanstack/react-query';
import "./KeyInsights.css"

import Loader from './Loader'
import { startCase } from 'lodash';
import growthIcon from '../assets/growth-audience.svg';

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

    const { data: companyData } = useQuery({
        queryKey: ['TopCompanies', selectedYear, selectedField, data],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/top-companies`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        year: selectedYear,
                        field: selectedField?.value || 'all'
                    })
                }
            )
            if (!response.ok) throw new Error("Failed to fetch top companies");
            return response.json();
        }
    })

    return (
        <div className="insights-card">
            {isLoading ? (<Loader />) : (
                <>

                    <div className="insights-header">
                        <span className="insights-icon">
                            <img src={growthIcon} alt="insights" width="20" height="20" />
                        </span>
                        <h3>Key Insights</h3>
                    </div>

                    {/* Divider */}
                    <div className="divider"></div>

                    {/* Insight 1 */}
                    <div className="insight">
                        <h4>{keydata.brief || ""}</h4>
                    </div>
                    <div className="highlighted-insight">
                        <p>{keydata.detail || ""}</p>

                    </div>

                    <div className="company-card">
                        <h3 className="top-companies-title">Top hiring companies</h3>
                        <div className="top-companies-list">
                            {companyData?.map((key, index) => (
                                <div key={index} className="top-company-container">
                                    <div className="top-company-info">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="top-company-icon">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3.75h.008v.008h-.008v-.008Zm0 3h.008v.008h-.008v-.008Zm0 3h.008v.008h-.008v-.008Z" />
                                        </svg>

                                        <h3 className="top-company-name">{startCase(key.company)}</h3>
                                    </div>
                                    <div className="top-company-badge">
                                        {key.count} Jobs
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                </>

            )}
        </div>

    );
}
export default Key_insights
