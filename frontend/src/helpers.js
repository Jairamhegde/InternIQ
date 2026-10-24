// shared helpers for api calls, formatting and chart settings
import { API_URL } from './config.js';

// api calls

export async function getJson(path) {
    const response = await fetch(`${API_URL}${path}`);
    if (!response.ok) {
        throw new Error(`Request failed: ${path}`);
    }
    return response.json();
}

export async function postJson(path, body) {
    const response = await fetch(`${API_URL}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    if (!response.ok) {
        throw new Error(`Request failed: ${path}`);
    }
    return response.json();
}

// text formatting

// words that normal title case gets wrong
const SPECIAL_WORDS = {
    ai: 'AI',
    ml: 'ML',
    aws: 'AWS',
    gcp: 'GCP',
    etl: 'ETL',
    sql: 'SQL',
    api: 'API',
    rest: 'REST',
    html: 'HTML',
    css: 'CSS',
    php: 'PHP',
    ui: 'UI',
    ux: 'UX',
    qa: 'QA',
    llm: 'LLM',
    cad: 'CAD',
    javascript: 'JavaScript',
    typescript: 'TypeScript',
    mysql: 'MySQL',
    postgresql: 'PostgreSQL',
    mongodb: 'MongoDB',
    devops: 'DevOps',
    'node.js': 'Node.js',
    'react.js': 'React.js',
    pytorch: 'PyTorch',
    tensorflow: 'TensorFlow',
    github: 'GitHub',
    fastapi: 'FastAPI',
    pyspark: 'PySpark',
};

// turn lowercase names into title case
export function toTitle(text) {
    if (text === null || text === undefined) {
        return '';
    }

    const words = String(text).trim().toLowerCase().split(' ');
    const titleWords = [];
    for (const word of words) {
        titleWords.push(capitalizeWord(word));
    }
    return titleWords.join(' ');
}

function capitalizeWord(word) {
    if (SPECIAL_WORDS[word]) {
        return SPECIAL_WORDS[word];
    }

    // short codes in brackets become uppercase
    const isShortCode = word.startsWith('(') && word.endsWith(')') && word.length <= 6;
    if (isShortCode) {
        return word.toUpperCase();
    }

    // skip a leading bracket before capitalizing
    if (word.startsWith('(')) {
        return '(' + word.charAt(1).toUpperCase() + word.slice(2);
    }

    return word.charAt(0).toUpperCase() + word.slice(1);
}

// number and date formatting

// number with indian digit grouping
export function formatNumber(value) {
    return Number(value).toLocaleString('en-IN');
}

// salary in full rupees
export function formatRupee(value) {
    return `₹${Math.round(Number(value)).toLocaleString('en-IN')}`;
}

// short month name
export function shortMonth(month) {
    const name = toTitle(month);
    return name.slice(0, 3);
}

// day and month
export function formatDay(isoDate) {
    const date = new Date(isoDate);
    return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
}

// how many days ago a job was posted
export function daysAgo(isoDate) {
    const millisecondsPerDay = 24 * 60 * 60 * 1000;

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const posted = new Date(isoDate);
    posted.setHours(0, 0, 0, 0);

    const days = Math.round((today - posted) / millisecondsPerDay);
    if (days <= 0) {
        return 'Today';
    }
    if (days === 1) {
        return '1 day ago';
    }
    return `${days} days ago`;
}

// chart settings

// one colour per series
export const CHART_COLORS = ['#6d9cf2', '#e59a5b', '#4fb79a', '#b18ceb', '#e0767f', '#d9c25e'];

// blue shades for the locations chart
export const BLUE_RAMP = ['#6d9cf2', '#5279c4', '#3d5b94', '#2d4369', '#24344f'];

export const AXIS_STYLE = {
    axisLine: false,
    tickLine: false,
    tick: { fill: '#7d8a9b', fontSize: 12 },
};

// brighter text for chart labels
export const LABEL_COLOR = '#c5cfdb';
export const LABEL_TICK = { fill: LABEL_COLOR, fontSize: 13 };

export const GRID_COLOR = '#263140';

// background behind the hovered bar
export const HOVER_CURSOR = { fill: 'rgba(109, 156, 242, 0.08)' };

// ring around the highlighted point
export const ACTIVE_DOT_RING = '#18202b';

export const SALARY_NOTE = 'Based only on postings that list a salary. Unpaid or unlisted are excluded.';
