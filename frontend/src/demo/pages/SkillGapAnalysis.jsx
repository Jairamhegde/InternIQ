import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Card, PageHeader, Icon, ErrorMessage } from '../components.jsx';
import { toTitle } from '../helpers.js';
import { API_URL } from '../../config.js';
import './SkillGapAnalysis.css';

const TARGET_FIELDS = [
    { value: 'backend', label: 'Backend' },
    { value: 'frontend', label: 'Frontend' },
    { value: 'mobile', label: 'Mobile' },
    { value: 'machine learning', label: 'Machine Learning' },
];

// Sends the resume as form data to /api/analyze-gap.
async function analyzeResume(field, resume) {
    const formData = new FormData();
    formData.append('field', field);
    formData.append('resume', resume);

    const response = await fetch(`${API_URL}/api/analyze-gap`, {
        method: 'POST',
        body: formData,
    });
    if (!response.ok) {
        throw new Error('Failed to connect to gap analyzer');
    }

    const result = await response.json();
    if (result.error) {
        throw new Error(result.error);
    }
    return result;
}

function SkillGapAnalysis() {
    const [field, setField] = useState('backend');
    const [resume, setResume] = useState(null);

    const analysis = useMutation({
        mutationFn: () => analyzeResume(field, resume),
    });

    function handleFileChange(event) {
        const files = event.target.files;
        if (files && files.length > 0) {
            setResume(files[0]);
            analysis.reset();
        }
    }

    let fileText = 'Choose a PDF or DOCX file';
    if (resume) {
        fileText = resume.name;
    }

    return (
        <>
            <PageHeader
                title="Skill Gap Analysis"
                description="Upload a resume to see how it matches current demand for a target field."
            />

            <Card title="Your resume" subtitle="The file is only used for this analysis">
                <div className="gap-form">
                    <label className="form-field">
                        <span className="form-label">Target field</span>
                        <select className="native-select" value={field} onChange={(event) => setField(event.target.value)}>
                            {TARGET_FIELDS.map((option) => (
                                <option key={option.value} value={option.value}>{option.label}</option>
                            ))}
                        </select>
                    </label>

                    <label className="form-field form-field-grow">
                        <span className="form-label">Resume</span>
                        <span className={resume ? 'file-picker has-file' : 'file-picker'}>
                            <Icon name={resume ? 'file' : 'upload'} size={16} />
                            <span className="file-picker-text">{fileText}</span>
                            <input type="file" accept=".pdf,.docx" onChange={handleFileChange} />
                        </span>
                    </label>

                    <button
                        className="btn btn-primary"
                        onClick={() => analysis.mutate()}
                        disabled={!resume || analysis.isPending}
                    >
                        {analysis.isPending ? 'Analyzing...' : 'Analyze'}
                    </button>
                </div>
            </Card>

            {analysis.isError && (
                <div className="card">
                    <ErrorMessage text={`Analysis failed: ${analysis.error.message}`} />
                </div>
            )}

            {analysis.data && <GapResult result={analysis.data} field={field} />}
        </>
    );
}

// ---------- Result: match score and skill lists ----------

function GapResult({ result, field }) {
    const matched = result.matched;
    const essential = result.missing.filter((skill) => skill.priority === 'e');
    const goodToHave = result.missing.filter((skill) => skill.priority === 'r');

    const totalSkills = matched.length + result.missing.length;
    let score = 0;
    if (totalSkills > 0) {
        score = Math.round((matched.length / totalSkills) * 100);
    }

    const fieldLabel = TARGET_FIELDS.find((option) => option.value === field).label;

    return (
        <>
            <Card title="Match score" subtitle={`Compared with skills asked for in ${fieldLabel} postings`}>
                <div className="score-row">
                    <span className="score-value">{score}%</span>
                    <span className="score-summary">
                        {matched.length} matched, {result.missing.length} missing
                    </span>
                </div>
                <div className="score-track">
                    <div className="score-fill" style={{ width: `${score}%` }} />
                </div>
            </Card>

            <div className="skill-columns">
                <SkillList title="Matched skills" skills={matched} tone="good" icon="check" />
                <SkillList title="Missing: essential" skills={essential} tone="bad" icon="close" />
                <SkillList title="Missing: good to have" skills={goodToHave} tone="neutral" icon="close" />
            </div>
        </>
    );
}

function SkillList({ title, skills, tone, icon }) {
    return (
        <Card title={title} subtitle={`${skills.length} skills`}>
            {skills.length === 0 ? (
                <p className="skill-none">None</p>
            ) : (
                <ul className="skill-list">
                    {skills.map((item) => (
                        <li key={item.skill} className={`skill skill-${tone}`}>
                            <Icon name={icon} size={14} />
                            {toTitle(item.skill)}
                        </li>
                    ))}
                </ul>
            )}
        </Card>
    );
}

export default SkillGapAnalysis;
