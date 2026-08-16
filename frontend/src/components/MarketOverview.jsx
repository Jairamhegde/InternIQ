
import { useState, useEffect } from 'react'
import "./MarketOverview.css"
import Loader from "./Loader"

function MarketOverview() {
    const [data, setData] = useState({})

    const [isLoading, setLoading] = useState(true)

    useEffect(() => {
        fetch(`http://localhost:8000/api/job-tiles`)
            .then((response) => response.json())
            .then((result) => { setData(result), setLoading(false) })
            .catch((error) => {
                console.log("Failed to connect to jobtile endpoint"), setLoading(false

                )
            })
    }, [])

    const stats = [
        {
            label: "TOTAL POSTINGS",
            value: data.year_posting || "...",
        },
        {
            label: "TRENDING TECHSTACK",
            value: data.skill || "...",
        },
        {
            label: "TOP LOCATION",
            value: data.location || "...",
        }
    ];

    return (
        <>
            {isLoading ? (<Loader />) : (
                <div className="market-overview">

                    <div className="market-overview-text">
                        <h2 className="market-title">State of the Market</h2>
                        <p className="market-description">
                            An analytical overview of the current hiring landscape,
                            tracking key volume indicators and compensation trends
                            across major domains.
                        </p>
                    </div>

                    <div className="overview-cards">
                        {stats.map((stat, index) => (
                            <div className="stat-card" key={index}>
                                <span className="stat-label">{stat.label}</span>
                                <div className="stat-value-row">
                                    <h3 className="stat-value">{stat.value}</h3>
                                </div>
                            </div>
                        ))}
                    </div>

                </div>


            )}


        </>
    );
}

export default MarketOverview;