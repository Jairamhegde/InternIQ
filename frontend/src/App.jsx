import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getJson, formatDay } from './helpers.js';
import './App.css';
import MarketOverview from './pages/MarketOverview.jsx';
import CompareRoles from './pages/CompareRoles.jsx';
import RoleDetails from './pages/RoleDetails.jsx';
import RecentTrends from './pages/RecentTrends.jsx';
import SkillGap from './pages/SkillGap.jsx';
import AskAI from './pages/AskAI.jsx';

const PAGES = [
    { id: 'overview', label: 'Overview' },
    { id: 'compare', label: 'Compare roles' },
    { id: 'role', label: 'Role details' },
    { id: 'trends', label: 'Last 10 days' },
    { id: 'skill-gap', label: 'Skill gap' },
    { id: 'ask-ai', label: 'Ask AI' },
];

// page from the url
function getPageFromUrl() {
    const hash = window.location.hash.replace('#', '');
    for (const page of PAGES) {
        if (page.id === hash) {
            return hash;
        }
    }
    return 'overview';
}

function App() {
    const [activePage, setActivePage] = useState(getPageFromUrl());

    // question sent from the overview ask box
    const [questionFromOverview, setQuestionFromOverview] = useState(null);

    function openPage(pageId) {
        setActivePage(pageId);
        window.location.hash = pageId;
        window.scrollTo({ top: 0 });
    }

    function askFromOverview(question) {
        setQuestionFromOverview({ text: question, id: Date.now() });
        openPage('ask-ai');
    }

    return (
        <div className="app">
            <TopBar activePage={activePage} onOpen={openPage} />
            <main className="page">
                <PageContent pageId={activePage} onOpen={openPage} onAsk={askFromOverview} question={questionFromOverview} />
            </main>
        </div>
    );
}

function PageContent({ pageId, onOpen, onAsk, question }) {
    if (pageId === 'compare') {
        return <CompareRoles />;
    }
    if (pageId === 'role') {
        return <RoleDetails />;
    }
    if (pageId === 'trends') {
        return <RecentTrends />;
    }
    if (pageId === 'skill-gap') {
        return <SkillGap />;
    }
    if (pageId === 'ask-ai') {
        return <AskAI questionFromOverview={question} />;
    }
    return <MarketOverview onOpen={onOpen} onAsk={onAsk} />;
}

function TopBar({ activePage, onOpen }) {
    return (
        <header className="topbar">
            <div className="topbar-inner">
                <button className="brand" onClick={() => onOpen('overview')}>
                    InternIQ
                </button>

                <nav className="topnav" aria-label="Pages">
                    {PAGES.map((page) => (
                        <button
                            key={page.id}
                            className="topnav-link"
                            aria-current={page.id === activePage ? 'page' : undefined}
                            onClick={() => onOpen(page.id)}
                        >
                            {page.label}
                        </button>
                    ))}
                </nav>

                <LastSync />
            </div>
        </header>
    );
}

// last sync status
function LastSync() {
    const { data, isError } = useQuery({
        queryKey: ['lastSync'],
        queryFn: () => getJson('/api/last-sync'),
    });

    let text = 'Checking';
    if (data) {
        text = `Updated ${formatDay(data.last_sync)}`;
    }
    if (isError) {
        text = 'Update time unavailable';
    }

    return (
        <span className="sync" title="Last time new postings were collected">
            <span className="sync-dot" />
            {text}
        </span>
    );
}

export default App;
