import React, { useEffect, useState } from 'react';
import "./SkillgapAnalysis.css"
import { API_URL } from '../config';
import { method } from 'lodash';

function SkillgapAnalysis() {
    const [selectedValue, setSelectedValue] = useState("backend");
    const [resume, setResume] = useState(null)
    const [gapData, setgapData] = useState(null)


    const Analyze = async () => {
        if (!resume) return;

        const formData = new FormData();
        formData.append("field", selectedValue)
        formData.append("resume", resume)

        try {
            const response = await fetch(`${API_URL}/api/analyze-gap`,
                {
                    method: 'POST',
                    body: formData,
                }
            );
            const result = await response.json()
            setgapData(result)
        } catch (error) {
            console.log("Failed to connect to gap-analyzer")
        }
    }

    // Calculate progress score safely
    const progressScore = gapData && gapData.matched ?
        Math.round((gapData.matched.length / (gapData.matched.length + gapData.missing.length)) * 100)
        : 0;

    // Filter missing skills by priority
    let missingEssential = [];
    let missingNiceToHave = [];

    if (gapData && gapData.missing) {
        missingEssential = gapData.missing.filter(obj => obj.priority === 'e');
        missingNiceToHave = gapData.missing.filter(obj => obj.priority === 'r');
    }



    return (

        <div className="skillgap-container">
            <div className="skillgap-header">
                <h1>Skill Gap Analysis</h1>
                <p>
                    Analyze the gap in your skills according to the target
                </p>
            </div>
            <div className='select-upload'>
                <SelectBox selectedValue={selectedValue} setSelectedValue={setSelectedValue} />
                <DocumentUpload resume={resume} setResume={setResume} />
                <button className='analyze-button' onClick={Analyze} disabled={!resume}>Analyze</button>

            </div>
            {gapData && (
                <>
                    <ProgressBar progressValue={progressScore} />
                    <div className='missing-matched-container'>
                        <div className='matched-skills'>
                            <h3 className="skills-heading">Matched Skills</h3>
                            <div className="skills-grid">
                                {gapData.matched.map((obj, index) => (
                                    <div className='skill-box matched' key={index}>
                                        <span className='symbol'>✓</span>
                                        <p>{obj.skill}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className='missing-skills'>
                            <h3 className="skills-heading">Missing Skills</h3>
                            <div className="skills-grid">
                                <div className='must-needed'>
                                    <p>Essential to have</p>
                                    <div className='skill-tile-holder'>
                                        {missingEssential.map((obj, index) => (
                                            <div className='skill-box missing' key={index}>
                                                <span className='symbol'>×</span>
                                                <p>{obj.skill}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div className='good-to-have'>
                                    <p>Good to have</p>
                                    <div className='skill-tile-holder'>
                                        {missingNiceToHave.map((obj, index) => (
                                            <div className='skill-box missing' key={index}>
                                                <span className='symbol'>×</span>
                                                <p>{obj.skill}</p>
                                            </div>
                                        ))}

                                    </div>

                                </div>

                            </div>
                        </div>
                    </div>
                </>

            )}

        </div>
    );
}

function SelectBox({ selectedValue, setSelectedValue }) {


    const fields = [
        { label: "Backend", value: 'backend' },
        { label: "Frontend", value: 'frontend' },
        { label: "Mobile", value: 'mobile' },
        { label: "Machine Learning", value: 'machine learning' },
    ]

    const handleChange = (e) => {
        setSelectedValue(e.target.value);
    };

    return (
        <div className="select-box">
            <select name="select" id="select" value={selectedValue} onChange={handleChange} className="custom-select">
                {fields.map((obj, index) => (
                    <option key={index} value={obj.value}>{obj.label}</option>
                ))}
            </select>
        </div>
    );
}


function DocumentUpload({ resume, setResume }) {
    const callHandler = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            setResume(e.target.files[0])
        }
    };
    return (
        <div className='doc-upload-container'>
            <div className='documnet-upload'>
                <input type="file" id='resume' accept='.pdf,.docx,.doc' onChange={callHandler} />
            </div>

        </div>
    );
}

function ProgressBar({ progressValue }) {
    return (
        <div className='progressbar-container'>
            <label>Match Score : {progressValue}%</label>
            <div className="progress-track">
                <div className="progress-fill" style={{ width: `${progressValue}%` }}></div>
            </div>
        </div>
    );
}

export default SkillgapAnalysis;