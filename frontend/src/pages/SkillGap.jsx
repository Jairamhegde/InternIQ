import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { PageLayout, Panel, ChipGroup, Loader, ErrorMessage, EmptyMessage } from '../components.jsx';
import { toTitle, formatNumber } from '../helpers.js';
import { API_URL } from '../config.js';

const TARGET_FIELDS = [
    { value: 'backend', label: 'Backend' },
    { value: 'frontend', label: 'Frontend' },
    { value: 'mobile', label: 'Mobile' },
    { value: 'machine learning', label: 'Machine learning' },
];

// send the resume to the gap analyzer
async function analyzeResume(field, resume) {
    const formData = new FormData();
    formData.append('field', field);
    formData.append('resume', resume);

    const response = await fetch(`${API_URL}/api/analyze-gap`, {
        method: 'POST',
        body: formData,
    });
    if (!response.ok) {
        throw new Error('Could not reach the resume checker. Please try again.');
    }

    const result = await response.json();
    if (result.error) {
        throw new Error(result.error);
    }
    return result;
}

function SkillGap() {
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

    function handleFieldChange(newField) {
        setField(newField);
        analysis.reset();
    }

    let fileText = 'Choose a file';
    if (resume) {
        fileText = resume.name;
    }

    let buttonText = 'Check my resume';
    if (analysis.isPending) {
        buttonText = 'Checking...';
    }

    const sidebar = (
        <>
            <ChipGroup label="Target field" options={TARGET_FIELDS} value={field} onChange={handleFieldChange} />
            <div className="filter-group">
                <span className="filter-label">Resume</span>
                <label className="file-drop" htmlFor="resume-file">
                    <strong>{fileText}</strong>
                    <span>PDF or DOCX</span>
                </label>
                <input id="resume-file" className="sr-only" type="file" accept=".pdf,.docx" onChange={handleFileChange} />
                <button
                    className="btn btn-primary btn-block"
                    disabled={!resume || analysis.isPending}
                    onClick={() => analysis.mutate()}
                >
                    {buttonText}
                </button>
                <p className="filter-hint">Your file is read for this check only and is not stored.</p>
            </div>
        </>
    );

    const fieldLabel = TARGET_FIELDS.find((option) => option.value === field).label;

    let content;
    if (analysis.isPending) {
        content = <Panel><Loader /></Panel>;
    } else if (analysis.isError) {
        content = <Panel><ErrorMessage text={analysis.error.message} /></Panel>;
    } else if (analysis.data) {
        content = <GapResult result={analysis.data} fieldLabel={fieldLabel} />;
    } else {
        content = (
            <Panel>
                <EmptyMessage
                    title="Check your resume"
                    text="Pick a target field, choose your resume and select Check my resume to see which skills you have and which are missing."
                />
            </Panel>
        );
    }

    return (
        <PageLayout
            title="Skill gap"
            description="Compare your resume with the skills employers ask for in your target field."
            sidebar={sidebar}
            sidebarTitle="Your resume"
        >
            {content}
        </PageLayout>
    );
}

// skill gap result

function GapResult({ result, fieldLabel }) {
    const matched = sortByDemand(result.matched);
    const askedOften = sortByDemand(result.missing.filter((skill) => skill.priority === 'e'));
    const askedLess = sortByDemand(result.missing.filter((skill) => skill.priority === 'r'));

    const totalSkills = matched.length + result.missing.length;
    let score = 0;
    if (totalSkills > 0) {
        score = Math.round((matched.length / totalSkills) * 100);
    }

    // two most asked missing skills
    const nextSkills = [];
    for (const item of askedOften.slice(0, 2)) {
        nextSkills.push(toTitle(item.skill));
    }

    let advice = '';
    if (nextSkills.length > 0) {
        advice = ` Adding ${nextSkills.join(' and ')} would close the biggest gaps.`;
    }

    return (
        <>
            <Panel title="Match score" subtitle={`Compared with the skills asked for in ${fieldLabel} postings`}>
                <div className="score">
                    <span className="score-value">{score}%</span>
                    <p className="score-text">
                        Your resume has {matched.length} of the {totalSkills} skills that {fieldLabel.toLowerCase()} postings ask for most.
                        {advice}
                    </p>
                </div>
                <div className="score-track" aria-hidden="true">
                    <div className="score-fill" style={{ width: `${score}%` }} />
                </div>
            </Panel>

            <div className="row row-3">
                <SkillList title="On your resume" skills={matched} tone="good" />
                <SkillList title="Missing, asked often" skills={askedOften} tone="bad" />
                <SkillList title="Missing, asked less" skills={askedLess} tone="neutral" />
            </div>
        </>
    );
}

// sort skills by demand
function sortByDemand(skills) {
    const sorted = [...skills];
    sorted.sort((first, second) => second.freq - first.freq);
    return sorted;
}

function SkillList({ title, skills, tone }) {
    let body;
    if (skills.length === 0) {
        body = <p className="cell-muted">None</p>;
    } else {
        body = (
            <ul className="skill-list">
                {skills.map((item) => (
                    <li key={item.skill}>
                        <span className="cell-strong">{toTitle(item.skill)}</span>
                        <span className="cell-muted">{formatNumber(item.freq)} postings</span>
                    </li>
                ))}
            </ul>
        );
    }

    return (
        <Panel title={title} subtitle={`${skills.length} skills`} className={`skill-panel tone-border-${tone}`}>
            {body}
        </Panel>
    );
}

export default SkillGap;
