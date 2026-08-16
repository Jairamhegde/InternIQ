
import { useState, useEffect } from 'react'
import "./MarketOverview.css"
import Loader from "./Loader"
import Select from 'react-select';
function MarketOverview({ data, setData, selectedField, setField }) {

    const [isLoading, setLoading] = useState(true)
    useEffect(() => {
        fetch(`http://localhost:8000/api/job-tiles?field=${selectedField}`)
            .then((response) => response.json())
            .then((result) => { setData(result), setLoading(false) })
            .catch((error) => {
                console.log("Failed to connect to jobtile endpoint"), setLoading(false

                )
            })
    }, [selectedField])

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
                    <div className='overview-sec1'>
                        <div className="market-overview-text">
                            <h2 className="market-title">State of the Market</h2>
                            <p className="market-description">
                                An analytical overview of the current hiring landscape,
                                tracking key volume indicators and compensation trends
                                across major domains.
                            </p>
                        </div>

                        <div className='selectBoxContainer'>
                            <SelectBox selectedField={selectedField} setField={setField} />
                        </div>
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


function SelectBox({ selectedField, setField }) {
    const myOptions = [
        { value: 'all', label: 'All' },
        { value: 'backend', label: 'Backend' },
        { value: 'frontend', label: 'Frontend ' },
        { value: 'mobile', label: 'Mobile' },
        { value: 'machine learning', label: 'Lachine Learning' },
        { value: 'data science', label: 'Data Science' },
        { value: 'big data', label: 'Big Data' },
        { value: 'fullstack', label: 'Fullstack' },

    ]

    const [isLoading, setLoading] = useState(false)


    const handleChange = (selected) => {
        setField(selected)

    };

    return (
        <div className="select-box-container">
            {isLoading ? (<Loader />) : (
                <>
                    <h3>
                        Select Field
                    </h3>
                    <Select
                        options={myOptions}
                        value={selectedField}
                        onChange={handleChange}
                        classNamePrefix='my-select'
                    />
                </>
            )}
        </div>
    );
}

export default MarketOverview;