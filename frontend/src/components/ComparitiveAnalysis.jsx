import { useState, useEffect } from 'react'
import "./ComparitiveAnalysis.css"
import Select from 'react-select';
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

import {
    Radar,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,

} from 'recharts';
import { result } from 'lodash';
import Loader from './Loader';


function ComparitiveAnalysis() {
    const [selectedJobs, setSelectedJobs] = useState([]);
    return (
        <div className='comparitive-analysis-page'>
            <div className='comparitive-header'>
                <h1>Comparitive Analysis</h1>
                <p>Compare multiple jobs across key metrics and trends</p>
            </div>
            <SelectBox selectedJobs={selectedJobs} setSelectedJobs
                ={setSelectedJobs} />



        </div>
    );
}


function SelectBox({ selectedJobs, setSelectedJobs }) {
    const [topRoles, setTopRoles] = useState([])
    const [isLoading, setLoading] = useState(true)

    useEffect(() => {
        fetch(`http://localhost:8000/api/top-role-table`)
            .then((response) => response.json())
            .then((result) => {
                const options = result.map((item) => ({
                    value: item.role,
                    label: item.role,
                }));
                setTopRoles(options);
                setLoading(false);
            })
            .catch((error) => { console.log("Failed to connect to top-role endpoint"); setLoading(false); })
    }, [])

    const handleChange = (selected) => {
        if (!selected || selected.length <= 3) {
            setSelectedJobs(selected || []);
        }
    };

    return (
        <div className="select-box-container">
            {isLoading ? (<Loader />) : (
                <>
                    <h3>
                        Select two or three job roles to compare
                    </h3>
                    <Select
                        options={topRoles}
                        isMulti
                        value={selectedJobs}
                        onChange={handleChange}
                        isOptionDisabled={() => selectedJobs.length >= 3}
                        placeholder="Search and select 2 to 3 roles..."
                    />
                    <div className="selection-status">
                        {selectedJobs.length < 2 ? (
                            <span className="status-hint warning">
                                Please select at least 2 roles (Selected: {selectedJobs.length}/3)
                            </span>
                        ) : (
                            <>
                                <span className="status-hint success">
                                    ✓ Ready for comparison ({selectedJobs.length}/3 selected)
                                </span>

                                <ComaparitiveCharts selectedJobs={selectedJobs} />
                            </>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
function ComaparitiveCharts({ selectedJobs }) {
    const [chartData, setChartData] = useState([])
    const [commonSkills, setCommonSkills] = useState([])

    const [compInsights, setInsights] = useState([])



    useEffect(() => {
        if (!selectedJobs || selectedJobs.length < 2) {
            setCommonSkills([])
            return;
        }

        const roleNames = selectedJobs.map(job => job.value || job)

        fetch(`http://localhost:8000/api/common-skill`,
            {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ roles: roleNames })
            }
        )
            .then((response) => response.json())
            .then((result) => setCommonSkills(result))
            .catch((err) => console.log("failed to connect to common skill endpoint"))
    }, [selectedJobs])


    useEffect(() => {
        if (!selectedJobs || selectedJobs.length < 2) {
            setChartData([])
            return;
        }

        const roleNames = selectedJobs.map(job => job.value || job)

        fetch(`http://localhost:8000/api/get-role-posting`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ roles: roleNames }),
            }
        )
            .then((response) => response.json())
            .then((result) => setChartData(result))
            .catch((error) => console.log("Failed to connect to role posting endpoint"))
    }, [selectedJobs])

    useEffect(() => {
        if (!chartData || chartData.length == 0
            || !commonSkills || commonSkills.length == 0
        ) {
            return;
        }
        fetch(`http://localhost:8000/api/get-comparitive-insights`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'Application/json',
                },
                body: JSON.stringify(
                    {
                        role_frequency: chartData,
                        common_skill: commonSkills
                    })
            }
        )
            .then((response) => response.json())
            .then((result) => setInsights(result))
            .then(() => console.log("Result fetch succesfully"))
            .catch((err) => console.log("Failed to connec to get-comparitive-insights", err))

    }, [chartData])

    return (
        <>
            <div className='comparitive-dashboard'>
                <div className='comparitive-chart'>
                    <div className='comp-header'>
                        <h3>Postings comparision</h3>
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
                            <XAxis dataKey='role' />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="volume" fill="#3f74e7"
                                label={{ position: 'top', fill: '#0f172a', fontSize: 13, fontWeight: 600 }} />

                        </BarChart>
                    </ResponsiveContainer>

                    <ComparitiveAnalysisInsights title="Insights" data={compInsights?.role_insights} />
                </div>
                <div className='Radar-chart'>
                    <div className='comp-header'>
                        <h3>Skills Comparison</h3>
                    </div>
                    <ResponsiveContainer width='100%' height={350}>
                        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={commonSkills}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey='skill' tickFormatter={startCase} />
                            <PolarRadiusAxis angle={30} domain={[0, 100]} />
                            {
                                selectedJobs.map((job, index) => {
                                    const title = job.value || job
                                    const colors = ['#3b82f6', '#10b981', '#f59e0b'];

                                    return (
                                        <Radar
                                            dataKey={title}
                                            name={startCase(title)}
                                            key={title}
                                            stroke={colors[index % colors.length]}
                                            fill={colors[index % colors.length]}
                                            fillOpacity={0.4}
                                        />
                                    )
                                })
                            }
                        </RadarChart>
                    </ResponsiveContainer>
                    <ComparitiveAnalysisInsights title="Insights" data={compInsights?.skill_insights} />

                </div>
            </div>
            <ComparitiveAnalysisInsights title="Key takeaway" data={compInsights?.takeaway} />

        </>
    );
}

function ComparitiveAnalysisInsights({ title, data }) {
    return (
        <div className='comp-insights-card'>
            <h3>{title}</h3>
            {data ? (
                <p>{data}</p>
            ) : (
                <p>...</p>
            )}
        </div>
    );
}

export default ComparitiveAnalysis;