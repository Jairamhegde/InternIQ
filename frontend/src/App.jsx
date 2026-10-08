import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Icon } from './components.jsx';
import { getJson } from './helpers.js';
import './App.css';
import MarketOverview from './pages/MarketOverview.jsx';
import ComparativeAnalysis from './pages/ComparativeAnalysis.jsx';
import RecentMarketTrend from './pages/RecentMarketTrend.jsx';
import SkillGapAnalysis from './pages/SkillGapAnalysis.jsx';
import RoleSpecificAnalysis from './pages/RoleSpecificAnalysis.jsx';
import AskAI from './pages/AskAI.jsx';

const ANALYTICS_PAGES = [
    { id: 'overview', label: 'Market Overview', icon: 'overview' },
    { id: 'compare', label: 'Compare Roles', icon: 'compare' },
    { id: 'role', label: 'Role Analysis', icon: 'role' },
    { id: 'trends', label: 'Recent Trends', icon: 'trend' },
    { id: 'skill-gap', label: 'Skill Gap', icon: 'gap' },
];

const ASSISTANT_PAGE = { id: 'ask-ai', label: 'Ask AI', icon: 'ai' };

// Opening /#trends goes straight to that page.
function getPageFromUrl() {
    const hash = window.location.hash.replace('#', '');
    if (hash === '') {
        return 'overview';
    }
    return hash;
}

function App() {
    const [activePage, setActivePage] = useState(getPageFromUrl());
    const [menuOpen, setMenuOpen] = useState(false);

    function openPage(pageId) {
        setActivePage(pageId);
        setMenuOpen(false);
        window.location.hash = pageId;
        window.scrollTo({ top: 0 });
    }

    return (
        <div className="shell">
            <aside className={menuOpen ? 'sidebar is-open' : 'sidebar'}>
                <div className="brand">
                    <span className="brand-mark">IQ</span>
                    <span className="brand-name">InternIQ</span>
                    <button className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle menu">
                        <Icon name="menu" size={20} />
                    </button>
                </div>

                <nav className="nav">
                    <span className="nav-section">Analytics</span>
                    {ANALYTICS_PAGES.map((page) => (
                        <NavItem key={page.id} page={page} activePage={activePage} onOpen={openPage} />
                    ))}

                    <span className="nav-section">Assistant</span>
                    <NavItem page={ASSISTANT_PAGE} activePage={activePage} onOpen={openPage} />
                </nav>

                <PipelineStatus />
            </aside>

            <main className="main">
                <div className="content">
                    <PageContent pageId={activePage} />
                </div>
            </main>
        </div>
    );
}

function PageContent({ pageId }) {
    if (pageId === 'compare') {
        return <ComparativeAnalysis />;
    }
    if (pageId === 'role') {
        return <RoleSpecificAnalysis />;
    }
    if (pageId === 'trends') {
        return <RecentMarketTrend />;
    }
    if (pageId === 'skill-gap') {
        return <SkillGapAnalysis />;
    }
    if (pageId === 'ask-ai') {
        return <AskAI />;
    }
    return <MarketOverview />;
}

function NavItem({ page, activePage, onOpen }) {
    const isActive = page.id === activePage;

    return (
        <button
            className={isActive ? 'nav-item is-active' : 'nav-item'}
            onClick={() => onOpen(page.id)}
            aria-current={isActive ? 'page' : undefined}
        >
            <Icon name={page.icon} size={18} />
            {page.label}
        </button>
    );
}

function PipelineStatus() {
    const { data, isError } = useQuery({
        queryKey: ['lastSync'],
        queryFn: () => getJson('/api/last-sync'),
    });

    let syncText = 'Checking...';
    if (data) {
        syncText = `Last sync ${data.last_sync}`;
    }
    if (isError) {
        syncText = 'Sync status unavailable';
    }

    return (
        <div className="sync">
            <span className={isError ? 'sync-dot is-offline' : 'sync-dot'} aria-hidden="true" />
            <div>
                <span className="sync-label">Pipeline status</span>
                <span className="sync-time">{syncText}</span>
            </div>
        </div>
    );
}

export default App;
