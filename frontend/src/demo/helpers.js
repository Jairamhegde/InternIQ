// Small helpers shared by every page of the demo dashboard.
import { API_URL } from '../config.js';

// ---------- API calls ----------

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

// ---------- Text and number formatting ----------

// The API returns text in mixed case, such as "data engineer" or "ai SPECIALIST".
// This makes every word start with a capital letter: "Data Engineer".
// Short codes in brackets stay upper case, so "(ai)" becomes "(AI)".
export function toTitle(text) {
    if (text === null || text === undefined) {
        return '';
    }

    const words = String(text).trim().toLowerCase().split(' ');
    const titleWords = words.map((word) => capitalizeWord(word));
    return titleWords.join(' ');
}

function capitalizeWord(word) {
    const isShortCode = word.startsWith('(') && word.endsWith(')') && word.length <= 6;
    if (isShortCode) {
        return word.toUpperCase();
    }

    // Skip a leading bracket so "(wfh/part" becomes "(Wfh/part".
    if (word.startsWith('(')) {
        return '(' + word.charAt(1).toUpperCase() + word.slice(2);
    }
    return word.charAt(0).toUpperCase() + word.slice(1);
}

export function formatNumber(value) {
    return Number(value).toLocaleString('en-IN');
}

export function formatRupee(value) {
    return `₹${Math.round(Number(value)).toLocaleString('en-IN')}`;
}

// The API pads month names ("may      "), so trim and shorten them to "May".
export function shortMonth(month) {
    const name = toTitle(month);
    return name.slice(0, 3);
}

// ---------- Chart settings ----------

// Muted chart colours, checked for colour-blind readability.
export const CHART_COLORS = ['#4a7fbf', '#d4784a', '#3f9c7c'];

// One blue ramp, darkest first, used where slices are ranked (the location pie chart).
export const BLUE_RAMP = ['#2f5f98', '#4a7fbf', '#7fa6d4', '#b3cbe7'];

export const AXIS_STYLE = {
    axisLine: false,
    tickLine: false,
    tick: { fill: '#8b8a83', fontSize: 12 },
};

export const GRID_COLOR = '#efeeea';
