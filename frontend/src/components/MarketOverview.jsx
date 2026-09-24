
import { useState, useEffect } from 'react'
import { API_URL } from '../config.js';
import { useQuery } from '@tanstack/react-query';
import "./MarketOverview.css"
import Loader from "./Loader"
import Select from 'react-select';


function MarketOverview({ data, setData, selectedField, setField }) {
    const { data: fetchedData = {}, isFetching } = useQuery({
        queryKey: ['marketOverview', selectedField.value],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/job-tiles?field=${selectedField.value}`);
            if (!response.ok) throw new Error("Failed to connect to jobtile endpoint");
            return response.json();
        }
    });

    useEffect(() => {
        if (Object.keys(fetchedData).length > 0) {
            setData(fetchedData);
        }
    }, [fetchedData, setData]);

    const stats = [
        {
            label: "OPPORTUNITIES TRACKED",
            value: data.year_posting || "...",
            cnt: "Postings",
        },
        {
            label: "TOP ROLE",
            value: data.role || "...",
            cnt: data.roleCount !== undefined ? `${data.roleCount} jobs` : "...",
        },
        {
            label: "MOST DEMANDED SKILL",
            value: data.skill || "...",
            cnt: data.skillCount !== undefined ? `${data.skillCount} mentions` : "...",
        },
        {
            label: "TOP LOCATION",
            value: data.location || "...",
            cnt: data.locationCount !== undefined ? `${data.locationCount} jobs` : "...",
        }
    ];

    return (
        <div className="market-overview">

            {/* <div className="market-overview-text">
                <h1 className="market-title">Internship Job Market Overview</h1>
                <p className="market-description">
                    An analytical overview of the current hiring landscape,
                    tracking key volume indicators and compensation trends
                    across major domains.
                </p>
            </div> */}

            <div className="overview-cards">
                {stats.map((stat, index) => (
                    <div
                        className="stat-card"
                        key={index}
                        style={{ opacity: isFetching ? 0.6 : 1 }}
                    >
                        <span className="stat-label">{stat.label}</span>
                        <div className="stat-value-row">
                            {isFetching ? <h4 className="stat-value">...</h4> :
                                <div className='tile-details'>
                                    <h4 className='stat-value' title={typeof stat.value === 'string' ? stat.value : ''}>
                                        {stat.value}
                                    </h4>
                                    <h5 className='stat-val'>
                                        <span className="stat-arrow"></span> {stat.cnt}
                                    </h5>
                                </div>
                            }
                        </div>
                    </div>
                ))}
                <div className='selectBoxContainer'>
                    <SelectBox selectedField={selectedField} setField={setField} />
                </div>
            </div>

        </div>
    );
}


function SelectBox({ selectedField, setField }) {
    const myOptions = [
        { value: 'all', label: 'All' },
        { value: 'backend', label: 'Backend' },
        { value: 'frontend', label: 'Frontend ' },
        { value: 'mobile', label: 'Mobile' },
        { value: 'machine learning', label: 'Machine Learning' },
        { value: 'data science', label: 'Data Science' },
        { value: 'big data', label: 'Big Data' },
        { value: 'fullstack', label: 'Fullstack' },

    ]

    const [isLoading, setLoading] = useState(false)


    const handleChange = (selected) => {
        setField(selected)

    };

    return (
        <div className="market-select-inner">
            {isLoading ? (<Loader />) : (
                <>
                    <h4>
                        Select Field
                    </h4>
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
